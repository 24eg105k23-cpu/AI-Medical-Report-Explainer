from sqlalchemy import create_engine
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError

from app.db.base import Base
from app.core.config import settings
from app.db.session import verify_database_connection
from app.models.audit_event import AuditEvent
from app.models.document import Document
from app.models.laboratory_value import LaboratoryValue
from app.models.ocr_result import OCRResult
from app.models.prescription_item import PrescriptionItem
from app.models.prescription_record import PrescriptionRecord
from app.models.rag_document_metadata import RAGDocumentMetadata
from app.models.reference_document import ReferenceDocument
from app.models.report_analysis import ReportAnalysis
from app.models.user import User


def test_database_url_escapes_special_characters():
    configured = settings.model_copy(
        update={
            "DB_USER": "app@local",
            "DB_PASSWORD": "a:/?#%b",
            "DB_MIGRATION_USER": "migrator@local",
            "DB_MIGRATION_PASSWORD": "migration:/?#%b",
        }
    )
    rendered = configured.DATABASE_URL.render_as_string(hide_password=False)
    parsed = make_url(rendered)
    migration_url = make_url(
        configured.MIGRATION_DATABASE_URL.render_as_string(hide_password=False)
    )

    assert parsed.drivername == "mysql+pymysql"
    assert parsed.username == "app@local"
    assert parsed.password == "a:/?#%b"
    assert parsed.database == "medical_report_db"
    assert migration_url.username == "migrator@local"
    assert migration_url.password == "migration:/?#%b"


def test_migrated_models_and_foreign_key_relationships(db_session):
    user = User(email="relational@example.test", password_hash="hash")
    reference = ReferenceDocument(
        title="Offline guide",
        publisher="Local",
        chunks_metadata=[{"text": "Hemoglobin"}],
    )
    db_session.add_all([user, reference])
    db_session.flush()

    document = Document(
        user_id=user.id,
        original_filename="report.pdf",
        storage_key="random.pdf",
        document_type="report",
        mime_type="application/pdf",
        file_size=100,
    )
    db_session.add(document)
    db_session.flush()

    ocr = OCRResult(document_id=document.id, extracted_text="Hb 13.5 g/dL")
    analysis = ReportAnalysis(document_id=document.id, explanation={})
    db_session.add_all([ocr, analysis])
    db_session.flush()

    lab_value = LaboratoryValue(
        analysis_id=analysis.id,
        test_name="Hemoglobin",
        value_text="13.50",
        numeric_value=13.5,
        unit="g/dL",
        source_location={},
    )
    prescription = PrescriptionRecord(document_id=document.id)
    db_session.add_all([lab_value, prescription])
    db_session.flush()

    medicine = PrescriptionItem(
        document_id=document.id,
        prescription_id=prescription.id,
        extracted_medicine_name="Example",
        confidence_metadata={},
    )
    audit = AuditEvent(user_id=user.id, event_type="test_event", safe_metadata={})
    reference.rag_metadata = RAGDocumentMetadata(
        retrieval_backend="mock",
        chunk_count=1,
        index_metadata={},
    )
    db_session.add_all([medicine, audit])
    db_session.flush()

    assert document.owner.id == user.id
    assert document.ocr_results[0].id == ocr.id
    assert document.analyses[0].laboratory_values[0].value_text == "13.50"
    assert document.prescription_items[0].prescription.id == prescription.id
    assert prescription.items[0].id == medicine.id
    assert reference.rag_metadata.chunk_count == 1
    assert audit.user.id == user.id


def test_database_unique_constraint_rejects_duplicate_user_email(db_session):
    db_session.add(User(email="unique@example.test", password_hash="one"))
    db_session.commit()
    db_session.add(User(email="unique@example.test", password_hash="two"))

    try:
        db_session.commit()
    except IntegrityError:
        db_session.rollback()
    else:
        raise AssertionError("Duplicate user email was accepted")

    assert db_session.query(User).filter_by(email="unique@example.test").count() == 1


def test_transaction_rollback_discards_pending_record(db_session):
    db_session.add(User(email="rollback@example.test", password_hash="hash"))
    db_session.rollback()

    assert db_session.query(User).filter_by(email="rollback@example.test").first() is None


def test_applied_migrations_match_sqlalchemy_models(db_session):
    migration_context = MigrationContext.configure(db_session.connection())
    differences = compare_metadata(migration_context, Base.metadata)

    assert differences == []


def test_connection_failure_has_actionable_message():
    broken_engine = create_engine(
        "mysql+pymysql://medical_app:unused@127.0.0.1:1/medical_report_test",
        connect_args={"connect_timeout": 1},
        pool_pre_ping=True,
    )
    try:
        try:
            verify_database_connection(broken_engine)
        except RuntimeError as exc:
            assert "Could not connect to the local MySQL database" in str(exc)
        else:
            raise AssertionError("An unavailable database reported a successful connection")
    finally:
        broken_engine.dispose()
