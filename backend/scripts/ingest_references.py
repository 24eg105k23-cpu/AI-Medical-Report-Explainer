"""Report reference documents explicitly ingested into the local database."""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.models.reference_document import ReferenceDocument


def main():
    print("=" * 60)
    print("AI Medical Report Explainer - Reference Document Ingestion")
    print("=" * 60)

    db = SessionLocal()
    try:
        docs = db.query(ReferenceDocument).all()
        print(f"Reference documents in database: {len(docs)}")
        for doc in docs:
            print(f"- [{doc.id[:8]}...] {doc.title} ({doc.publisher}) | {len(doc.chunks_metadata)} chunks")

        if not docs:
            print("No references have been ingested. No demo references were added.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
