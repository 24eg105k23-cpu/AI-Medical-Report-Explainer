from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid, utc_now

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.laboratory_value import LaboratoryValue


class ReportAnalysis(Base):
    __tablename__ = "report_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    analysis_status: Mapped[str] = mapped_column(String(50), default="completed", nullable=False)
    structured_results: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    explanation: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    model_provider: Mapped[str] = mapped_column(String(50), default="mock", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="analyses")
    laboratory_values: Mapped[List["LaboratoryValue"]] = relationship(
        "LaboratoryValue",
        back_populates="analysis",
        cascade="all, delete-orphan",
    )
