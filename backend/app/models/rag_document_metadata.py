from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid, utc_now


class RAGDocumentMetadata(Base):
    __tablename__ = "rag_document_metadata"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    reference_document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("reference_documents.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    retrieval_backend: Mapped[str] = mapped_column(String(50), default="local_tfidf", nullable=False)
    vector_index_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    chunk_count: Mapped[int] = mapped_column(default=0, nullable=False)
    index_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    reference_document: Mapped["ReferenceDocument"] = relationship(
        "ReferenceDocument",
        back_populates="rag_metadata",
    )
