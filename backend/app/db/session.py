from pathlib import Path
from typing import Generator
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
    pool_size=settings.MYSQL_POOL_SIZE,
    max_overflow=settings.MYSQL_MAX_OVERFLOW,
    pool_timeout=settings.MYSQL_POOL_TIMEOUT,
    pool_recycle=settings.MYSQL_POOL_RECYCLE,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """Dependency for obtaining database session per request"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_database_connection(database_engine: Engine = engine) -> str:
    """Verify MySQL connectivity and return the server version."""
    try:
        with database_engine.connect() as connection:
            return str(connection.execute(text("SELECT VERSION()")).scalar_one())
    except SQLAlchemyError as exc:
        raise RuntimeError(
            "Could not connect to the local MySQL database. Confirm MySQL is running, "
            "DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD are correct, and the database "
            "setup SQL has been applied."
        ) from exc


def verify_database_schema_current(connection) -> bool:
    """Return whether an open database connection is at the current Alembic heads."""
    backend_dir = Path(__file__).resolve().parents[2]
    alembic_config = Config(str(backend_dir / "alembic.ini"))
    alembic_config.set_main_option("script_location", str(backend_dir / "alembic"))
    expected_heads = set(ScriptDirectory.from_config(alembic_config).get_heads())
    current_heads = set(MigrationContext.configure(connection).get_current_heads())
    return current_heads == expected_heads
