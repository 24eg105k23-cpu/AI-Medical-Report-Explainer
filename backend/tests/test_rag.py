from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.reference_document import ReferenceDocument
from app.schemas.analysis import SourceReferenceSchema
from app.services.rag_service import rag_service


def test_rag_retrieval_and_source_metadata(db_session: Session):
    rag_service.initialize_reference_corpus(db_session)
    retrieved = rag_service.retrieve_relevant_sources(db_session, query="Hemoglobin red blood cells anemia", top_k=2)

    assert len(retrieved) > 0
    top_source, chunk_text, score = retrieved[0]
    assert "CBC" in top_source.title or "Blood" in top_source.title
    assert top_source.publisher != ""
    assert top_source.chunk_id is not None
    assert score > 0.0


def test_rag_citation_validation_rejects_hallucinated_sources():
    """
    Ensure the RAG service strictly prevents fabricated citations.
    """
    genuinely_retrieved = [
        SourceReferenceSchema(
            title="Complete Blood Count (CBC) Guide",
            publisher="MedlinePlus",
            chunk_id="hematology_1",
        )
    ]

    hallucinated_citations = [
        SourceReferenceSchema(
            title="Invented Medical Journal 2026",
            publisher="Fake Publisher",
            chunk_id="fake_chunk_99",
        ),
        SourceReferenceSchema(
            title="Complete Blood Count (CBC) Guide",
            publisher="MedlinePlus",
            chunk_id="hematology_1",
        ),
    ]

    filtered = rag_service.validate_citations(
        cited_sources=hallucinated_citations,
        retrieved_sources=genuinely_retrieved,
    )

    # Fake journal must be rejected
    assert len(filtered) == 1
    assert filtered[0].title == "Complete Blood Count (CBC) Guide"


def test_reference_sources_endpoint(client: TestClient):
    response = client.get("/api/v1/reference-sources")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) >= 5
    titles = [d["title"] for d in data]
    assert any("Complete Blood Count" in t for t in titles)


def test_medical_explanation_endpoint(client: TestClient, auth_headers_user_one: dict):
    response = client.post(
        "/api/v1/explanations",
        json={"query": "What does a high Hemoglobin level indicate?"},
        headers=auth_headers_user_one,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["query"] == "What does a high Hemoglobin level indicate?"
    assert len(data["explanation"]) > 20
    assert "disclaimer" in data
    assert len(data["sources"]) > 0
