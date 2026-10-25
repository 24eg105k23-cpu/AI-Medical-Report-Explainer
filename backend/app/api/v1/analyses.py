import hashlib
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, get_user_analysis, get_user_document
from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.document import Document
from app.models.laboratory_value import LaboratoryValue
from app.models.ocr_result import OCRResult
from app.models.report_analysis import ReportAnalysis
from app.models.user import User
from app.schemas.analysis import (
    AnalysisCreateRequest,
    LaboratoryValueSchema,
    ReportAnalysisResponse,
    SourceReferenceSchema,
    StructuredExplanationSchema,
)
from app.schemas.common import APIResponse
from app.services.audit_service import AuditService
from app.services.llm_service import get_llm_provider
from app.services.rag_service import rag_service
from app.services.report_parser import report_parser

logger = get_logger("analyses_api")
router = APIRouter(tags=["Medical Report Analysis"])


def _analysis_response(analysis: ReportAnalysis, db: Session) -> ReportAnalysisResponse:
    lab_vals = db.query(LaboratoryValue).filter(LaboratoryValue.analysis_id == analysis.id).all()
    parsed_vals = [
        LaboratoryValueSchema(
            id=value.id,
            test_name=value.test_name,
            value_text=value.value_text,
            numeric_value=value.numeric_value,
            unit=value.unit,
            reference_range=value.reference_range,
            abnormality_status=value.abnormality_status,
            source_location=value.source_location,
            verification_status=value.verification_status,
        )
        for value in lab_vals
    ]
    explanation = StructuredExplanationSchema(**analysis.explanation)
    return ReportAnalysisResponse(
        id=analysis.id,
        document_id=analysis.document_id,
        analysis_status=analysis.analysis_status,
        model_provider=analysis.model_provider,
        created_at=analysis.created_at,
        summary=explanation.summary,
        stats=analysis.structured_results.get("stats", {}),
        laboratory_values=parsed_vals,
        explanation=explanation,
        sources=explanation.source_citations,
    )


@router.post(
    "/documents/{document_id}/analyze",
    response_model=APIResponse[ReportAnalysisResponse],
    summary="Analyze a medical report, extract lab values, and generate plain-language AI explanation",
)
def analyze_document(
    document_id: str,
    request: AnalysisCreateRequest = AnalysisCreateRequest(),
    document: Document = Depends(get_user_document),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    1. Retrieve the extracted report text (or user-edited text).
    2. Parse lines into structured laboratory values (values, units, reference intervals, abnormality flags).
    3. Retrieve relevant medical reference information via RAG.
    4. Generate a patient-friendly plain-language explanation using LLM.
    5. Enforce strict citation validation (only cite retrieved documents).
    6. Save analysis and laboratory values to database.
    """
    # 1. Fetch latest OCR result
    ocr_rec = (
        db.query(OCRResult)
        .filter(OCRResult.document_id == document.id)
        .order_by(OCRResult.created_at.desc())
        .first()
    )
    if not ocr_rec or not ocr_rec.extracted_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has no extracted text to analyze. Please upload a clear document or enter text manually.",
        )

    text_hash = hashlib.sha256(ocr_rec.extracted_text.encode("utf-8")).hexdigest()
    if not request.force_reanalyze:
        cached_analysis = (
            db.query(ReportAnalysis)
            .filter(ReportAnalysis.document_id == document.id)
            .order_by(ReportAnalysis.created_at.desc())
            .first()
        )
        cached_options = (cached_analysis.structured_results or {}) if cached_analysis else {}
        if (
            cached_analysis
            and cached_options.get("source_text_sha256") == text_hash
            and cached_options.get("include_rag_sources") == request.include_rag_sources
            and cached_analysis.model_provider == settings.LLM_PROVIDER
        ):
            return APIResponse(
                success=True,
                message="Existing analysis returned; set force_reanalyze to generate it again.",
                data=_analysis_response(cached_analysis, db),
            )

    # 2. Parse report text into structured lab values
    parsed_values, parse_meta = report_parser.parse_report_text(ocr_rec.extracted_text)

    # 3. Construct RAG retrieval query based on detected tests
    if parsed_values:
        query_terms = [v.test_name for v in parsed_values]
        rag_query = " ".join(query_terms)
    else:
        rag_query = ocr_rec.extracted_text[:300]

    retrieved_chunk_tuples = (
        rag_service.retrieve_relevant_sources(db, query=rag_query, top_k=settings.VECTOR_SEARCH_TOP_K)
        if request.include_rag_sources
        else []
    )
    retrieved_sources = [item[0] for item in retrieved_chunk_tuples]
    retrieved_context = [
        {
            "source": source.model_dump(mode="json"),
            "passage": passage,
            "score": score,
        }
        for source, passage, score in retrieved_chunk_tuples
    ]

    # 4. Generate structured explanation via LLM provider
    llm = get_llm_provider()
    explanation_schema: StructuredExplanationSchema = llm.generate_explanation(
        lab_values=parsed_values,
        retrieved_sources=retrieved_sources,
        raw_text_snippet=ocr_rec.extracted_text[:1000],
        retrieved_context=retrieved_context,
    )

    # 5. Strict citation validation
    validated_citations = rag_service.validate_citations(
        cited_sources=explanation_schema.source_citations,
        retrieved_sources=retrieved_sources,
    )
    explanation_schema.source_citations = validated_citations

    # 6. Save ReportAnalysis
    analysis = ReportAnalysis(
        document_id=document.id,
        analysis_status="completed",
        structured_results={
            "stats": parse_meta["stats"],
            "total_detected": len(parsed_values),
            "source_text_sha256": text_hash,
            "include_rag_sources": request.include_rag_sources,
        },
        explanation=explanation_schema.model_dump(),
        model_provider=settings.LLM_PROVIDER,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # 7. Save LaboratoryValue records
    saved_lab_values: List[LaboratoryValueSchema] = []
    for val in parsed_values:
        ref_dict = val.reference_range.model_dump() if val.reference_range else None
        loc_dict = val.source_location.model_dump() if val.source_location else {}

        db_val = LaboratoryValue(
            analysis_id=analysis.id,
            test_name=val.test_name,
            value_text=val.value_text,
            numeric_value=val.numeric_value,
            unit=val.unit,
            reference_range=ref_dict,
            abnormality_status=val.abnormality_status,
            source_location=loc_dict,
            verification_status=val.verification_status,
        )
        db.add(db_val)
        db.commit()
        db.refresh(db_val)

        val.id = db_val.id
        saved_lab_values.append(val)

    document.processing_status = "completed"
    db.commit()

    AuditService.record_event(
        db=db,
        event_type="report_analyzed",
        user_id=current_user.id,
        resource_id=analysis.id,
        metadata={"tests_count": len(saved_lab_values), "abnormal_count": parse_meta["stats"]["abnormal"]},
    )

    response_data = ReportAnalysisResponse(
        id=analysis.id,
        document_id=document.id,
        analysis_status=analysis.analysis_status,
        model_provider=analysis.model_provider,
        created_at=analysis.created_at,
        summary=explanation_schema.summary,
        stats=parse_meta["stats"],
        laboratory_values=saved_lab_values,
        explanation=explanation_schema,
        sources=validated_citations,
    )

    return APIResponse(
        success=True,
        message="Medical report analyzed and grounded explanation generated successfully.",
        data=response_data,
    )


@router.get(
    "/analyses/{analysis_id}",
    response_model=APIResponse[ReportAnalysisResponse],
    summary="Get analysis results by ID",
)
def get_analysis(
    analysis: ReportAnalysis = Depends(get_user_analysis),
    db: Session = Depends(get_db),
):
    """
    Retrieve completed report analysis, structured findings, and source citations.
    """
    return APIResponse(
        success=True,
        message="Analysis retrieved successfully.",
        data=_analysis_response(analysis, db),
    )


@router.get(
    "/documents/{document_id}/values",
    response_model=APIResponse[List[LaboratoryValueSchema]],
    summary="Get extracted laboratory values for a document",
)
def get_document_values(
    document: Document = Depends(get_user_document),
    db: Session = Depends(get_db),
):
    """
    Retrieve laboratory values for the latest analysis of a document.
    """
    latest_analysis = (
        db.query(ReportAnalysis)
        .filter(ReportAnalysis.document_id == document.id)
        .order_by(ReportAnalysis.created_at.desc())
        .first()
    )
    if not latest_analysis:
        return APIResponse(
            success=True,
            message="No analysis performed yet for this document.",
            data=[],
        )

    lab_vals = db.query(LaboratoryValue).filter(LaboratoryValue.analysis_id == latest_analysis.id).all()
    results = [
        LaboratoryValueSchema(
            id=lv.id,
            test_name=lv.test_name,
            value_text=lv.value_text,
            numeric_value=lv.numeric_value,
            unit=lv.unit,
            reference_range=lv.reference_range,
            abnormality_status=lv.abnormality_status,
            source_location=lv.source_location,
            verification_status=lv.verification_status,
        )
        for lv in lab_vals
    ]

    return APIResponse(
        success=True,
        message="Laboratory values retrieved.",
        data=results,
    )


@router.get(
    "/analyses/{analysis_id}/sources",
    response_model=APIResponse[List[SourceReferenceSchema]],
    summary="Get trusted reference sources cited by an analysis",
)
def get_analysis_sources(
    analysis: ReportAnalysis = Depends(get_user_analysis),
):
    explanation_obj = StructuredExplanationSchema(**analysis.explanation)
    return APIResponse(
        success=True,
        message="Reference sources fetched successfully.",
        data=explanation_obj.source_citations,
    )
