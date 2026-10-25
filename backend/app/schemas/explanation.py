from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.analysis import SourceReferenceSchema


class ExplanationRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Medical term, test name, or plain language question")
    context_values: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Optional list of lab values to provide context for the explanation",
    )


class ExplanationResponse(BaseModel):
    query: str
    explanation: str
    key_points: List[str] = Field(default_factory=list)
    suggested_doctor_questions: List[str] = Field(default_factory=list)
    sources: List[SourceReferenceSchema] = Field(default_factory=list)
    disclaimer: str = (
        "Educational medical information only. Not a medical consultation or diagnosis. "
        "Please discuss your specific results with your physician."
    )


class ReferenceSourceResponse(BaseModel):
    id: str
    title: str
    publisher: str
    source_url: Optional[str] = None
    revision_date: Optional[str] = None
    ingestion_status: str
    chunk_count: int
