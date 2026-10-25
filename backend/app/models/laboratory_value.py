from datetime import datetime
from typing import Any, Dict, Optional, TYPE_CHECKING
from sqlalchemy import DateTime, Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid, utc_now

if TYPE_CHECKING:
    from app.models.report_analysis import ReportAnalysis


class LaboratoryValue(Base):
    __tablename__ = "laboratory_values"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    analysis_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("report_analyses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    test_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    value_text: Mapped[str] = mapped_column(String(100), nullable=False)
    numeric_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    reference_range: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    abnormality_status: Mapped[str] = mapped_column(
        String(50),
        default="unavailable",
        nullable=False,
    )  # "normal" | "high" | "low" | "abnormal" | "unavailable"
    source_location: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="needs_review",
        nullable=False,
    )  # "extracted" | "verified" | "user_corrected" | "needs_review"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    analysis: Mapped["ReportAnalysis"] = relationship("ReportAnalysis", back_populates="laboratory_values")
