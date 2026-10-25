from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, get_user_document
from app.core.exceptions import AppError
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.document import Document
from app.models.ocr_result import OCRResult
from app.models.user import User
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.document import (
    DocumentResponse,
    DocumentStatusResponse,
    DocumentTextResponse,
    DocumentTextUpdateRequest,
)
from app.services.audit_service import AuditService
from app.services.document_extraction import document_extractor
from app.services.document_storage import document_storage

logger = get_logger("documents_api")
router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=APIResponse[DocumentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload a medical report or prescription document",
)
async def upload_document(
    file: UploadFile = File(..., description="PDF, PNG, or JPEG file"),
    document_type: str = Form("report", description="'report' or 'prescription'"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Securely upload a document, validate headers and magic byte signatures,
    store the file safely outside the public web root, and trigger automatic text extraction/OCR.
    """
    if document_type not in ("report", "prescription"):
        document_type = "report"

    # Read uploaded bytes
    content = await file.read()
    filename = file.filename or "uploaded_document"

    try:
        # Validate file size, extension, MIME type, and magic bytes
        normalized_mime = document_storage.validate_file(
            filename=filename,
            content=content,
            content_type=file.content_type or "",
        )

        # Store file safely
        storage_key, absolute_path = document_storage.save_file(
            content=content,
            original_filename=filename,
            mime_type=normalized_mime,
        )
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected upload failure: {e}")
        raise HTTPException(status_code=500, detail="Failed to process document upload.")

    # Create document record
    doc = Document(
        user_id=current_user.id,
        original_filename=filename,
        storage_key=storage_key,
        document_type=document_type,
        mime_type=normalized_mime,
        file_size=len(content),
        processing_status="processing",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Perform immediate OCR / Text extraction
    try:
        extracted_text, metadata, extraction_status = document_extractor.extract_text(
            file_path=Path(absolute_path),
            mime_type=normalized_mime,
        )

        ocr_rec = OCRResult(
            document_id=doc.id,
            extracted_text=extracted_text,
            extraction_status=extraction_status,
            extraction_metadata=metadata,
        )
        db.add(ocr_rec)
        doc.processing_status = "extracted"
        db.commit()
        db.refresh(doc)
    except Exception as e:
        logger.error(f"Text extraction failed for doc {doc.id}: {e}")
        doc.processing_status = "extraction_failed"
        db.commit()

    AuditService.record_event(
        db=db,
        event_type="document_uploaded",
        user_id=current_user.id,
        resource_id=doc.id,
        metadata={"filename": doc.original_filename, "file_size": doc.file_size, "type": doc.document_type},
    )

    return APIResponse(
        success=True,
        message="Document uploaded and text extracted successfully.",
        data=DocumentResponse.model_validate(doc),
    )


@router.get(
    "",
    response_model=APIResponse[PaginatedResponse[DocumentResponse]],
    summary="List all uploaded documents for current user",
)
def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    document_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Document).filter(Document.user_id == current_user.id)
    if document_type:
        query = query.filter(Document.document_type == document_type)

    total = query.count()
    items = (
        query.order_by(Document.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return APIResponse(
        success=True,
        message="Documents retrieved successfully.",
        data=PaginatedResponse(
            items=[DocumentResponse.model_validate(d) for d in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        ),
    )


@router.get(
    "/{document_id}",
    response_model=APIResponse[DocumentResponse],
    summary="Get single document details",
)
def get_document(
    document: Document = Depends(get_user_document),
):
    return APIResponse(
        success=True,
        message="Document fetched successfully.",
        data=DocumentResponse.model_validate(document),
    )


@router.get(
    "/{document_id}/status",
    response_model=APIResponse[DocumentStatusResponse],
    summary="Get processing status of document",
)
def get_document_status(
    document: Document = Depends(get_user_document),
    db: Session = Depends(get_db),
):
    ocr_exists = db.query(OCRResult).filter(OCRResult.document_id == document.id).first() is not None
    return APIResponse(
        success=True,
        message="Status retrieved.",
        data=DocumentStatusResponse(
            id=document.id,
            processing_status=document.processing_status,
            original_filename=document.original_filename,
            document_type=document.document_type,
            has_extracted_text=ocr_exists,
            has_analysis=len(document.analyses) > 0,
        ),
    )


@router.get(
    "/{document_id}/text",
    response_model=APIResponse[DocumentTextResponse],
    summary="Get extracted OCR text for user review",
)
def get_document_text(
    document: Document = Depends(get_user_document),
    db: Session = Depends(get_db),
):
    ocr_rec = (
        db.query(OCRResult)
        .filter(OCRResult.document_id == document.id)
        .order_by(OCRResult.created_at.desc())
        .first()
    )
    if not ocr_rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No extracted text found for this document.",
        )

    return APIResponse(
        success=True,
        message="Extracted text fetched for review.",
        data=DocumentTextResponse(
            document_id=document.id,
            extracted_text=ocr_rec.extracted_text,
            extraction_status=ocr_rec.extraction_status,
            metadata=ocr_rec.extraction_metadata,
            can_edit=True,
        ),
    )


@router.patch(
    "/{document_id}/text",
    response_model=APIResponse[DocumentTextResponse],
    summary="Correct or edit extracted OCR text before running analysis",
)
def update_document_text(
    update_data: DocumentTextUpdateRequest,
    document: Document = Depends(get_user_document),
    db: Session = Depends(get_db),
):
    """
    Allow user to review and correct OCR errors before triggering clinical report parsing.
    """
    ocr_rec = (
        db.query(OCRResult)
        .filter(OCRResult.document_id == document.id)
        .order_by(OCRResult.created_at.desc())
        .first()
    )
    if not ocr_rec:
        ocr_rec = OCRResult(
            document_id=document.id,
            extracted_text=update_data.extracted_text,
            extraction_status="user_corrected",
            extraction_metadata={"edited": True},
        )
        db.add(ocr_rec)
    else:
        ocr_rec.extracted_text = update_data.extracted_text
        ocr_rec.extraction_status = "user_corrected"
        meta = dict(ocr_rec.extraction_metadata)
        meta["user_edited"] = True
        ocr_rec.extraction_metadata = meta

    document.processing_status = "extracted"
    db.commit()
    db.refresh(ocr_rec)

    AuditService.record_event(
        db=db,
        event_type="document_text_corrected",
        user_id=document.user_id,
        resource_id=document.id,
    )

    return APIResponse(
        success=True,
        message="Document text updated successfully.",
        data=DocumentTextResponse(
            document_id=document.id,
            extracted_text=ocr_rec.extracted_text,
            extraction_status=ocr_rec.extraction_status,
            metadata=ocr_rec.extraction_metadata,
            can_edit=True,
        ),
    )


@router.delete(
    "/{document_id}",
    response_model=APIResponse[None],
    summary="Delete document and related derived data",
)
def delete_document(
    document: Document = Depends(get_user_document),
    db: Session = Depends(get_db),
):
    """
    Delete document, associated OCR, analyses, and physically remove stored file from disk.
    """
    storage_key = document.storage_key
    doc_id = document.id
    user_id = document.user_id

    db.delete(document)
    db.commit()

    # Physically delete file
    document_storage.delete_file(storage_key)

    AuditService.record_event(
        db=db,
        event_type="document_deleted",
        user_id=user_id,
        resource_id=doc_id,
    )

    return APIResponse(
        success=True,
        message="Document and all associated analyses deleted successfully.",
        data=None,
    )
