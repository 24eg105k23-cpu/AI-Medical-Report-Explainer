from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_filename: str
    document_type: str
    mime_type: str
    file_size: int
    processing_status: str
    created_at: datetime


class DocumentStatusResponse(BaseModel):
    id: str
    processing_status: str
    original_filename: str
    document_type: str
    has_extracted_text: bool
    has_analysis: bool


class DocumentTextResponse(BaseModel):
    document_id: str
    extracted_text: str
    extraction_status: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    can_edit: bool = True


class DocumentTextUpdateRequest(BaseModel):
    extracted_text: str = Field(..., min_length=1, description="Updated or corrected report text")
