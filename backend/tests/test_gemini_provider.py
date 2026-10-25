import json

import httpx
import pytest

from app.core.config import settings
from app.core.exceptions import LLMServiceError
from app.schemas.analysis import StructuredExplanationSchema
from app.services.llm_service import GeminiLLMProvider, get_llm_provider


def test_gemini_report_request_uses_header_and_validates_json(monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setattr(settings, "GEMINI_MODEL", "gemini-test-model")
    monkeypatch.setattr(settings, "GEMINI_TIMEOUT_SECONDS", 180.0)
    client_timeouts = []
    response_body = {
        "summary": "The report contains no detected values.",
        "test_explanations": [],
        "key_findings": [],
        "questions_for_doctor": [],
        "uncertainties_or_missing_context": [],
        "source_citations": [],
        "medical_disclaimer": "Educational information only.",
    }

    def handler(request):
        assert request.headers["x-goog-api-key"] == "test-gemini-key"
        assert "test-gemini-key" not in str(request.url)
        assert request.url.path.endswith("/models/gemini-test-model:generateContent")
        body = request.read().decode()
        assert '"responseMimeType":"application/json"' in body
        return httpx.Response(
            200,
            json={"candidates": [{"content": {"parts": [{"text": json.dumps(response_body)}]}}]},
        )

    real_client = httpx.Client
    transport = httpx.MockTransport(handler)

    def create_client(**kwargs):
        client_timeouts.append(kwargs["timeout"])
        return real_client(transport=transport, **kwargs)

    monkeypatch.setattr(
        "app.services.llm_service.httpx.Client",
        create_client,
    )

    result = GeminiLLMProvider().generate_explanation([], [])

    assert isinstance(result, StructuredExplanationSchema)
    assert result.summary == response_body["summary"]
    assert client_timeouts == [180.0]


def test_gemini_provider_selection_and_missing_key_error(monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")

    provider = get_llm_provider()
    assert isinstance(provider, GeminiLLMProvider)
    with pytest.raises(LLMServiceError, match="GEMINI_API_KEY"):
        provider.answer_query("What is hemoglobin?", [])


def test_gemini_api_failure_is_not_silently_replaced(monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "test-gemini-key")
    real_client = httpx.Client
    transport = httpx.MockTransport(
        lambda _request: httpx.Response(429, json={"error": {"message": "rate limited"}})
    )
    monkeypatch.setattr(
        "app.services.llm_service.httpx.Client",
        lambda **kwargs: real_client(transport=transport, **kwargs),
    )

    with pytest.raises(LLMServiceError, match="rate limit or quota"):
        GeminiLLMProvider().answer_query("What is hemoglobin?", [])


def test_gemini_timeout_is_reported_as_timeout(monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "test-gemini-key")
    real_client = httpx.Client

    def handler(_request):
        raise httpx.ReadTimeout("test timeout")

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(
        "app.services.llm_service.httpx.Client",
        lambda **kwargs: real_client(transport=transport, **kwargs),
    )

    with pytest.raises(LLMServiceError, match="timed out"):
        GeminiLLMProvider().answer_query("What is hemoglobin?", [])
