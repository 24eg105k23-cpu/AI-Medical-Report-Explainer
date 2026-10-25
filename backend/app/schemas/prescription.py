from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class PrescriptionItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    extracted_medicine_name: str
    extracted_strength: Optional[str] = None
    extracted_instructions: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    route: Optional[str] = None
    prescriber: Optional[str] = None
    prescription_date: Optional[str] = None
    confidence_metadata: Dict[str, Any] = Field(default_factory=dict)
    verification_status: str  # "pending_confirmation" | "confirmed_by_user" | "rejected"
    created_at: datetime


class PrescriptionConfirmRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    confirmed_medicine_name: Optional[str] = Field(default=None, min_length=1)
    confirmed_strength: Optional[str] = None
    confirmed_instructions: Optional[str] = None
    status: Literal["confirmed_by_user", "rejected"] = "confirmed_by_user"
    user_note: Optional[str] = None


class PrescriptionListResponse(BaseModel):
    document_id: str
    total_items: int
    items: List[PrescriptionItemResponse]
    requires_human_review: bool
    safety_notice: str = (
        "Educational prototype only. Medication data extracted by OCR may contain inaccuracies. "
        "Do not alter or commence any medication regimen without direct confirmation from a licensed clinician."
    )
