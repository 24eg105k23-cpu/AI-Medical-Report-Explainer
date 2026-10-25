from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ReferenceRangeSchema(BaseModel):
    low: Optional[float] = None
    high: Optional[float] = None
    text_range: Optional[str] = None
    unit: Optional[str] = None


class SourceLocationSchema(BaseModel):
    page: Optional[int] = 1
    line: Optional[int] = None
    snippet: Optional[str] = None


class LaboratoryValueSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = None
    test_name: str
    value_text: str
    numeric_value: Optional[float] = None
    unit: Optional[str] = None
    reference_range: Optional[ReferenceRangeSchema] = None
    abnormality_status: str = "unavailable"  # "normal" | "high" | "low" | "abnormal" | "unavailable"
    source_location: Optional[SourceLocationSchema] = None
    verification_status: str = "needs_review"  # "extracted" | "verified" | "user_corrected" | "needs_review"


class SourceReferenceSchema(BaseModel):
    document_id: Optional[str] = None
    title: str
    publisher: str
    source_url: Optional[str] = None
    revision_date: Optional[str] = None
    section: Optional[str] = None
    chunk_id: Optional[str] = None


class TestExplanationItem(BaseModel):
    test_name: str
    what_it_measures: str
    patient_value_summary: str
    reference_interval_explanation: str
    status_indication: str  # "Normal" | "High" | "Low" | "Requires Context"
    educational_note: str


class StructuredExplanationSchema(BaseModel):
    summary: str
    test_explanations: List[TestExplanationItem] = Field(default_factory=list)
    key_findings: List[str] = Field(default_factory=list)
    questions_for_doctor: List[str] = Field(default_factory=list)
    uncertainties_or_missing_context: List[str] = Field(default_factory=list)
    source_citations: List[SourceReferenceSchema] = Field(default_factory=list)
    medical_disclaimer: str = (
        "Educational prototype only. This summary does not provide medical diagnoses, "
        "treatment decisions, or medication advice. Always consult a qualified healthcare "
        "professional for clinical interpretation."
    )


class ReportAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    analysis_status: str
    model_provider: str
    created_at: datetime
    summary: str
    stats: Dict[str, int] = Field(default_factory=dict)
    laboratory_values: List[LaboratoryValueSchema] = Field(default_factory=list)
    explanation: StructuredExplanationSchema
    sources: List[SourceReferenceSchema] = Field(default_factory=list)


class AnalysisCreateRequest(BaseModel):
    force_reanalyze: bool = False
    include_rag_sources: bool = True
