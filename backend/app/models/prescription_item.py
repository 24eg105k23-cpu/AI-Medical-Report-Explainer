from datetime import datetime
from typing import Any, Dict, Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid, utc_now

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.prescription_record import PrescriptionRecord


class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    prescription_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("prescription_records.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    extracted_medicine_name: Mapped[str] = mapped_column(String(255), nullable=False)
    extracted_strength: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    extracted_instructions: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    frequency: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    duration: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    route: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    prescriber: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    prescription_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    confidence_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="pending_confirmation",
        nullable=False,
    )  # "pending_confirmation" | "confirmed_by_user" | "rejected"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="prescription_items")
    prescription: Mapped[Optional["PrescriptionRecord"]] = relationship(
        "PrescriptionRecord",
        back_populates="items",
    )
