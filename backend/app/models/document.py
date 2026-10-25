from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid, utc_now

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.ocr_result import OCRResult
    from app.models.report_analysis import ReportAnalysis
    from app.models.prescription_item import PrescriptionItem


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), default="report", nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    processing_status: Mapped[str] = mapped_column(String(50), default="uploaded", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="documents")
    ocr_results: Mapped[List["OCRResult"]] = relationship(
        "OCRResult",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    analyses: Mapped[List["ReportAnalysis"]] = relationship(
        "ReportAnalysis",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    prescriptions: Mapped[List["PrescriptionItem"]] = relationship(
        "PrescriptionItem",
        back_populates="document",
        cascade="all, delete-orphan",
    )
