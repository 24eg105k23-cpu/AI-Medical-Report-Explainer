from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import DateTime, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid, utc_now

if TYPE_CHECKING:
    from app.models.rag_document_metadata import RAGDocumentMetadata


class ReferenceDocument(Base):
    __tablename__ = "reference_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    publisher: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    revision_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ingestion_status: Mapped[str] = mapped_column(String(50), default="ingested", nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    chunks_metadata: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    rag_metadata: Mapped[Optional["RAGDocumentMetadata"]] = relationship(
        "RAGDocumentMetadata",
        back_populates="reference_document",
        cascade="all, delete-orphan",
        uselist=False,
    )
