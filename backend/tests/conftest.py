import os
import sys
from pathlib import Path
from typing import Generator

backend_root = Path(__file__).resolve().parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User
from app.services.rag_service import rag_service

# Use in-memory SQLite for testing to ensure complete isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    with TestingSessionLocal() as db:
        rag_service.initialize_reference_corpus(db)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def user_one(db_session: Session) -> User:
    user = User(
        email="patient_one@example.com",
        password_hash=hash_password("PatientOneSecret123!"),
        account_status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_two(db_session: Session) -> User:
    user = User(
        email="patient_two@example.com",
        password_hash=hash_password("PatientTwoSecret123!"),
        account_status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers_user_one(user_one: User) -> dict:
    token = create_access_token(subject=user_one.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_user_two(user_two: User) -> dict:
    token = create_access_token(subject=user_two.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_reports_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "sample_reports"
