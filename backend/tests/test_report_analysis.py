from pathlib import Path
from fastapi.testclient import TestClient
from app.schemas.analysis import StructuredExplanationSchema
from app.services.llm_service import MockLLMProvider
from app.services.report_parser import report_parser


def test_structured_report_parsing_cbc(sample_reports_dir: Path):
    text = (
        "Hemoglobin 13.5 g/dL 12.0 - 16.0\n"
        "WBC Count 12.4 10^3/uL 4.5 - 11.0 HIGH\n"
        "Platelet Count 240 10^3/uL 150 - 450\n"
    )
    values, meta = report_parser.parse_report_text(text)
    assert len(values) == 3

    # Check Hemoglobin
    hb = next(v for v in values if v.test_name == "Hemoglobin")
    assert hb.numeric_value == 13.5
    assert hb.unit == "g/dL"
    assert hb.reference_range is not None
    assert hb.reference_range.low == 12.0
    assert hb.reference_range.high == 16.0
    assert hb.abnormality_status == "normal"

    # Check WBC Count
    wbc = next(v for v in values if v.test_name == "WBC Count")
    assert wbc.numeric_value == 12.4
    assert wbc.abnormality_status == "high"


def test_missing_reference_range_not_invented(client: TestClient, auth_headers_user_one: dict, sample_reports_dir: Path):
    """
    CRITICAL REQUIREMENT:
    'If the report does not provide a reference interval, represent it as unavailable instead of inventing one.'
    """
    pdf_path = sample_reports_dir / "synthetic_missing_ranges_report.pdf"
    assert pdf_path.exists()

    with open(pdf_path, "rb") as f:
        up_resp = client.post(
            "/api/v1/documents/upload",
            files={"file": ("synthetic_missing_ranges_report.pdf", f.read(), "application/pdf")},
            headers=auth_headers_user_one,
        )
    assert up_resp.status_code == 201
    doc_id = up_resp.json()["data"]["id"]

    # Run analysis
    an_resp = client.post(f"/api/v1/documents/{doc_id}/analyze", headers=auth_headers_user_one)
    assert an_resp.status_code == 200
    data = an_resp.json()["data"]

    for val in data["laboratory_values"]:
        # Reference range MUST BE None / null because the report had no reference range
        assert val["reference_range"] is None
        assert val["abnormality_status"] == "unavailable"

    # Check that explanation mentions the missing reference intervals
    uncertainties = data["explanation"]["uncertainties_or_missing_context"]
    assert any("reference interval" in u.lower() or "reference" in u.lower() for u in uncertainties)


def test_mock_ai_explanation_schema_validation():
    """
    Verify MockLLMProvider produces output strictly valid according to StructuredExplanationSchema
    without requiring external paid API keys.
    """
    mock_provider = MockLLMProvider()
    values, _ = report_parser.parse_report_text("Hemoglobin 13.5 g/dL 12.0 - 16.0 NORMAL")

    result = mock_provider.generate_explanation(lab_values=values, retrieved_sources=[])
    assert isinstance(result, StructuredExplanationSchema)
    assert len(result.test_explanations) == 1
    assert "Hemoglobin" in result.test_explanations[0].test_name
    assert result.medical_disclaimer is not None
    assert len(result.questions_for_doctor) > 0


def test_get_document_values_endpoint(client: TestClient, auth_headers_user_one: dict, sample_reports_dir: Path):
    pdf_path = sample_reports_dir / "synthetic_cbc_report.pdf"
    with open(pdf_path, "rb") as f:
        up_resp = client.post(
            "/api/v1/documents/upload",
            files={"file": ("synthetic_cbc_report.pdf", f.read(), "application/pdf")},
            headers=auth_headers_user_one,
        )
    doc_id = up_resp.json()["data"]["id"]

    # Analyze
    client.post(f"/api/v1/documents/{doc_id}/analyze", headers=auth_headers_user_one)

    # Fetch values
    val_resp = client.get(f"/api/v1/documents/{doc_id}/values", headers=auth_headers_user_one)
    assert val_resp.status_code == 200
    values = val_resp.json()["data"]
    assert len(values) >= 3
    test_names = [v["test_name"] for v in values]
    assert "Hemoglobin" in test_names
