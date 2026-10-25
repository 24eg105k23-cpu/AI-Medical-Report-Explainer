from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.rag_document_metadata import RAGDocumentMetadata
from app.models.reference_document import ReferenceDocument
from app.schemas.analysis import SourceReferenceSchema
from app.services.rag_service import MockRetriever, SimpleTFIDFEmbedding, rag_service


def test_offline_retrieval_strategies_are_deterministic():
    mock = MockRetriever()
    local_score = SimpleTFIDFEmbedding.compute_similarity(
        "hemoglobin red blood cells",
        "hemoglobin is measured in red blood cells",
    )

    assert mock.score("hemoglobin levels", "hemoglobin is a blood measurement") == 1.0
    assert mock.score("unrelated", "hemoglobin is a blood measurement") == 0.0
    assert 0.0 < local_score <= 1.0


def test_rag_retrieval_and_source_metadata(db_session: Session):
    reference = ReferenceDocument(
        title="CBC lab guide",
        publisher="Test publisher",
        source_url="https://example.test/cbc",
        chunks_metadata=[{
            "chunk_id": "cbc_1",
            "section": "Hematology",
            "text": "Hemoglobin is measured in red blood cells. CBC anemia laboratory values.",
        }],
    )
    reference.rag_metadata = RAGDocumentMetadata(
        retrieval_backend="local_tfidf",
        chunk_count=1,
        index_metadata={},
    )
    db_session.add(reference)
    db_session.flush()
    retrieved = rag_service.retrieve_relevant_sources(db_session, query="Hemoglobin red blood cells anemia", top_k=2)

    assert len(retrieved) == 1
    top_source, chunk_text, score = retrieved[0]
    assert top_source.title == "CBC lab guide"
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
    assert data == []


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
    assert data["sources"] == []
