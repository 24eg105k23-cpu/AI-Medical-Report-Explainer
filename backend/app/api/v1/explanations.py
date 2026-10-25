from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.reference_document import ReferenceDocument
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.explanation import (
    ExplanationRequest,
    ExplanationResponse,
    ReferenceSourceResponse,
)
from app.services.llm_service import get_llm_provider
from app.services.rag_service import rag_service

router = APIRouter(tags=["RAG & Medical Explanations"])


@router.post(
    "/explanations",
    response_model=APIResponse[ExplanationResponse],
    summary="Get plain-language explanation of medical terms or tests grounded in RAG references",
)
def get_medical_explanation(
    request: ExplanationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Explain medical terminology or lab test parameters in plain language using RAG.
    Sources are strictly validated against retrieved references.
    """
    # 1. Retrieve trusted references via RAG
    chunk_tuples = rag_service.retrieve_relevant_sources(
        db,
        query=request.query,
        top_k=settings.VECTOR_SEARCH_TOP_K,
    )
    retrieved_sources = [item[0] for item in chunk_tuples]
    retrieved_context = [
        {
            "source": source.model_dump(mode="json"),
            "passage": passage,
            "score": score,
        }
        for source, passage, score in chunk_tuples
    ]

    # 2. Query LLM provider with grounding context
    llm = get_llm_provider()
    res = llm.answer_query(
        query=request.query,
        retrieved_sources=retrieved_sources,
        context_values=request.context_values,
        retrieved_context=retrieved_context,
    )

    # 3. Validate citations strictly
    validated_sources = rag_service.validate_citations(
        cited_sources=res.get("sources", []),
        retrieved_sources=retrieved_sources,
    )

    return APIResponse(
        success=True,
        message="Medical explanation generated successfully.",
        data=ExplanationResponse(
            query=request.query,
            explanation=res["explanation"],
            key_points=res.get("key_points", []),
            suggested_doctor_questions=res.get("suggested_doctor_questions", []),
            sources=validated_sources,
            disclaimer=res.get("disclaimer", "Educational prototype only. Always consult a healthcare professional."),
        ),
    )


@router.get(
    "/reference-sources",
    response_model=APIResponse[List[ReferenceSourceResponse]],
    summary="List all trusted medical reference documents ingested in RAG",
)
def list_reference_sources(
    db: Session = Depends(get_db),
):
    """
    List trusted medical references indexed in the knowledge base.
    """
    docs = db.query(ReferenceDocument).all()
    results = [
        ReferenceSourceResponse(
            id=d.id,
            title=d.title,
            publisher=d.publisher,
            source_url=d.source_url,
            revision_date=d.revision_date,
            ingestion_status=d.ingestion_status,
            chunk_count=len(d.chunks_metadata),
        )
        for d in docs
    ]

    return APIResponse(
        success=True,
        message="Reference sources retrieved successfully.",
        data=results,
    )
