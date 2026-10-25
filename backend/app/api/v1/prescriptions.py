from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.dependencies import (
    get_current_user,
    get_user_document,
    get_user_prescription_item,
)
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.document import Document
from app.models.ocr_result import OCRResult
from app.models.prescription_item import PrescriptionItem
from app.models.prescription_record import PrescriptionRecord
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.prescription import (
    PrescriptionConfirmRequest,
    PrescriptionItemResponse,
    PrescriptionListResponse,
)
from app.services.audit_service import AuditService
from app.services.prescription_parser import prescription_parser

logger = get_logger("prescriptions_api")
router = APIRouter(tags=["Prescription Processing"])


@router.post(
    "/documents/{document_id}/process-prescription",
    response_model=APIResponse[PrescriptionListResponse],
    summary="Process prescription document, extract medications, and flag uncertain fields",
)
def process_prescription(
    document_id: str,
    document: Document = Depends(get_user_document),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Extract structured medication items, preserving original text snippets.
    Flags uncertain medicine names and dosages for human confirmation.
    """
    ocr_rec = (
        db.query(OCRResult)
        .filter(OCRResult.document_id == document.id)
        .order_by(OCRResult.created_at.desc())
        .first()
    )
    if not ocr_rec or not ocr_rec.extracted_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prescription document has no extracted text. Please ensure the upload is clear or provide text manually.",
        )

    parsed_items = prescription_parser.parse_prescription_text(ocr_rec.extracted_text)
    db.query(PrescriptionItem).filter(
        PrescriptionItem.document_id == document.id
    ).delete(synchronize_session=False)
    prescription = (
        db.query(PrescriptionRecord)
        .filter(PrescriptionRecord.document_id == document.id)
        .first()
    )
    if prescription is None:
        prescription = PrescriptionRecord(document_id=document.id)
        db.add(prescription)
        db.flush()
    if parsed_items:
        prescription.prescriber = parsed_items[0].get("prescriber")
        prescription.prescription_date = parsed_items[0].get("prescription_date")

    saved_items: List[PrescriptionItemResponse] = []
    requires_human_review = False

    for item in parsed_items:
        db_item = PrescriptionItem(
            document_id=document.id,
            prescription_id=prescription.id,
            extracted_medicine_name=item["extracted_medicine_name"],
            extracted_strength=item.get("extracted_strength"),
            extracted_instructions=item.get("extracted_instructions"),
            frequency=item.get("frequency"),
            duration=item.get("duration"),
            route=item.get("route"),
            prescriber=item.get("prescriber"),
            prescription_date=item.get("prescription_date"),
            confidence_metadata=item.get("confidence_metadata", {}),
            verification_status=item.get("verification_status", "pending_confirmation"),
        )
        db.add(db_item)

        if db_item.confidence_metadata.get("needs_human_confirmation"):
            requires_human_review = True

        saved_items.append(db_item)

    document.processing_status = "prescription_processed"
    db.commit()
    for item in saved_items:
        db.refresh(item)

    AuditService.record_event(
        db=db,
        event_type="prescription_processed",
        user_id=current_user.id,
        resource_id=document.id,
        metadata={"items_count": len(saved_items)},
    )

    return APIResponse(
        success=True,
        message="Prescription medications extracted. Please review and confirm highlighted fields.",
        data=PrescriptionListResponse(
            document_id=document.id,
            total_items=len(saved_items),
            items=[PrescriptionItemResponse.model_validate(item) for item in saved_items],
            requires_human_review=requires_human_review,
        ),
    )


@router.get(
    "/documents/{document_id}/prescription",
    response_model=APIResponse[PrescriptionListResponse],
    summary="Get extracted medications for prescription document",
)
def get_document_prescription(
    document: Document = Depends(get_user_document),
    db: Session = Depends(get_db),
):
    items = (
        db.query(PrescriptionItem)
        .filter(PrescriptionItem.document_id == document.id)
        .order_by(PrescriptionItem.created_at.asc())
        .all()
    )

    res_items = [PrescriptionItemResponse.model_validate(it) for it in items]
    requires_review = any(
        it.verification_status == "pending_confirmation" or it.confidence_metadata.get("needs_human_confirmation")
        for it in items
    )

    return APIResponse(
        success=True,
        message="Prescription items retrieved.",
        data=PrescriptionListResponse(
            document_id=document.id,
            total_items=len(res_items),
            items=res_items,
            requires_human_review=requires_review,
        ),
    )


@router.patch(
    "/prescriptions/{prescription_id}/confirm",
    response_model=APIResponse[PrescriptionItemResponse],
    summary="Confirm or correct an extracted prescription item",
)
def confirm_prescription_item(
    confirm_data: PrescriptionConfirmRequest,
    item: PrescriptionItem = Depends(get_user_prescription_item),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Allow user to verify or rectify an extracted medication name, strength, or dosage instructions.
    Addresses requirement: Never silently convert uncertain handwriting into a confirmed medicine.
    """
    if (
        "confirmed_medicine_name" in confirm_data.model_fields_set
        and confirm_data.confirmed_medicine_name is not None
    ):
        item.extracted_medicine_name = confirm_data.confirmed_medicine_name
    if "confirmed_strength" in confirm_data.model_fields_set:
        item.extracted_strength = confirm_data.confirmed_strength
    if "confirmed_instructions" in confirm_data.model_fields_set:
        item.extracted_instructions = confirm_data.confirmed_instructions

    item.verification_status = confirm_data.status
    meta = dict(item.confidence_metadata)
    meta["user_reviewed"] = True
    meta["user_confirmed"] = confirm_data.status == "confirmed_by_user"
    if confirm_data.user_note:
        meta["user_note"] = confirm_data.user_note
    item.confidence_metadata = meta

    db.commit()
    db.refresh(item)

    AuditService.record_event(
        db=db,
        event_type="prescription_item_reviewed",
        user_id=current_user.id,
        resource_id=item.id,
        metadata={"status": item.verification_status},
    )

    return APIResponse(
        success=True,
        message="Prescription item confirmation saved.",
        data=PrescriptionItemResponse.model_validate(item),
    )
