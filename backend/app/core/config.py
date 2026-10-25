import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "AI Medical Report Explainer"
    APP_ENV: str = "development"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"

    # Security & JWT
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    ALGORITHM: str = "HS256"

    # Database
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_NAME: str = "medical_report_db"
    DB_USER: str = "medical_app"
    DB_PASSWORD: str = ""
    DB_MIGRATION_USER: str = "medical_migrator"
    DB_MIGRATION_PASSWORD: str = ""
    MYSQL_POOL_SIZE: int = 5
    MYSQL_MAX_OVERFLOW: int = 10
    MYSQL_POOL_TIMEOUT: int = 30
    MYSQL_POOL_RECYCLE: int = 1800

    # File Uploads
    UPLOAD_DIR: str = "./data/uploads"
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB default
    ALLOWED_MIME_TYPES: Union[List[str], str] = [
        "application/pdf",
        "image/png",
        "image/jpeg",
    ]

    # AI & LLM Service
    LLM_PROVIDER: str = "mock"  # "mock" | "gemini" | "openai" | "custom_http"
    MOCK_AI_RESPONSE_DELAY: float = 0.05
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.8-flash"
    GEMINI_TIMEOUT_SECONDS: float = 180.0
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    CUSTOM_LLM_ENDPOINT: str = ""
    CUSTOM_LLM_API_KEY: str = ""

    # RAG & Reference Docs
    REFERENCE_DOCS_DIR: str = "./data/references"
    EMBEDDING_PROVIDER: str = "mock"
    RETRIEVAL_MODE: str = "local_tfidf"
    VECTOR_SEARCH_TOP_K: int = 4

    # OCR Engine
    OCR_ENGINE: str = "auto"  # "auto" | "pymupdf" | "tesseract"
    TESSERACT_CMD: str = ""

    @property
    def DATABASE_URL(self) -> URL:
        """Build a MySQL URL from discrete values so credentials are escaped safely."""
        return URL.create(
            "mysql+pymysql",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
            query={"charset": "utf8mb4"},
        )

    @property
    def MIGRATION_DATABASE_URL(self) -> URL:
        """Build a separate MySQL URL for the Alembic schema owner."""
        return URL.create(
            "mysql+pymysql",
            username=self.DB_MIGRATION_USER,
            password=self.DB_MIGRATION_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
            query={"charset": "utf8mb4"},
        )

    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    @field_validator("ALLOWED_MIME_TYPES", mode="before")
    @classmethod
    def parse_allowed_mime_types(cls, v):
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                return [item.strip() for item in v.split(",") if item.strip()]
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                return [item.strip() for item in v.split(",") if item.strip()]
        return v


settings = Settings()
