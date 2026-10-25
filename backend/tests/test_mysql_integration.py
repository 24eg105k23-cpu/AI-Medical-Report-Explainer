import os
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from pathlib import Path

from app.models.document import Document
from app.models.user import User


MYSQL_TEST_DATABASE_URL = os.getenv("MYSQL_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not MYSQL_TEST_DATABASE_URL,
    reason="Set MYSQL_TEST_DATABASE_URL to the dedicated local medical_report_test database",
)


def _test_engine():
    url = make_url(MYSQL_TEST_DATABASE_URL)
    if url.drivername != "mysql+pymysql":
        raise ValueError("MySQL tests require a mysql+pymysql URL")
    if url.host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("MySQL integration tests are restricted to a local server")
    if not (url.database.startswith("test_") or url.database.endswith("_test")):
        raise ValueError("Refusing destructive migrations without a test-only database name")
    return create_engine(url, pool_pre_ping=True)


def test_mysql_connection_and_migrations():
    engine = _test_engine()
    try:
        with engine.connect() as connection:
            version = connection.execute(text("SELECT VERSION()")).scalar_one()
            assert version

        backend_dir = Path(__file__).resolve().parents[1]
        config = Config(str(backend_dir / "alembic.ini"))
        config.set_main_option("script_location", str(backend_dir / "alembic"))
        with engine.connect() as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, "head")
            assert connection.execute(text("SELECT 1 FROM alembic_version")).scalar_one()
    finally:
        engine.dispose()


def test_mysql_crud_duplicate_rollback_and_user_isolation():
    engine = _test_engine()
    test_token = uuid4().hex
    owner_email = f"mysql-owner-{test_token}@example.test"
    other_email = f"mysql-other-{test_token}@example.test"
    rollback_email = f"mysql-rollback-{test_token}@example.test"
    storage_key = f"mysql-test-{test_token}.pdf"
    try:
        with Session(engine) as session:
            orphan = Document(
                user_id=uuid4().hex,
                original_filename="orphan.pdf",
                storage_key=f"orphan-{test_token}.pdf",
                document_type="report",
                mime_type="application/pdf",
                file_size=20,
            )
            session.add(orphan)
            with pytest.raises(IntegrityError):
                session.flush()
            session.rollback()

            user = User(email=owner_email, password_hash="test-hash")
            session.add(user)
            session.commit()
            session.refresh(user)

            document = Document(
                user_id=user.id,
                original_filename="mysql-test.pdf",
                storage_key=storage_key,
                document_type="report",
                mime_type="application/pdf",
                file_size=20,
            )
            session.add(document)
            session.commit()
            session.refresh(document)

            assert document.owner.email == owner_email
            other_user = User(email=other_email, password_hash="test-hash")
            session.add(other_user)
            session.commit()
            assert session.query(Document).filter_by(user_id=other_user.id).count() == 0

            duplicate = User(email=user.email, password_hash="other")
            session.add(duplicate)
            with pytest.raises(IntegrityError):
                session.flush()
            session.rollback()

            rolled_back = User(email=rollback_email, password_hash="hash")
            session.add(rolled_back)
            session.rollback()
            assert session.query(User).filter_by(email=rollback_email).first() is None
    finally:
        with Session(engine) as session:
            session.query(Document).filter_by(storage_key=storage_key).delete()
            session.query(User).filter(
                User.email.in_([owner_email, other_email, rollback_email])
            ).delete(synchronize_session=False)
            session.commit()
        engine.dispose()
