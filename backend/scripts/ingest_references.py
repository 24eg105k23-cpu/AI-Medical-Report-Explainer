"""
Administrative script to ingest or re-index trusted medical reference documents into RAG database.
"""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.services.rag_service import rag_service
from app.models.reference_document import ReferenceDocument


def main():
    print("=" * 60)
    print("AI Medical Report Explainer - Reference Document Ingestion")
    print("=" * 60)

    db = SessionLocal()
    try:
        count = rag_service.initialize_reference_corpus(db)
        print(f"Total reference documents in database: {count}")

        docs = db.query(ReferenceDocument).all()
        for doc in docs:
            print(f"- [{doc.id[:8]}...] {doc.title} ({doc.publisher}) | {len(doc.chunks_metadata)} chunks")

        print("Reference corpus ingestion verified successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
