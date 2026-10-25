import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "AI Medical Report Explainer"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Security & JWT
    SECRET_KEY: str = "dev-secret-key-medical-report-explainer-mock-prototype"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = "sqlite:///./medical_explainer.db"

    # File Uploads
    UPLOAD_DIR: str = "./data/uploads"
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB default
    ALLOWED_MIME_TYPES: Union[List[str], str] = [
        "application/pdf",
        "image/png",
        "image/jpeg",
    ]

    # AI & LLM Service
    LLM_PROVIDER: str = "mock"  # "mock" | "openai" | "anthropic" | "custom_http"
    MOCK_AI_RESPONSE_DELAY: float = 0.05
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    CUSTOM_LLM_ENDPOINT: str = ""
    CUSTOM_LLM_API_KEY: str = ""

    # RAG & Reference Docs
    REFERENCE_DOCS_DIR: str = "./data/references"
    EMBEDDING_PROVIDER: str = "mock"
    VECTOR_SEARCH_TOP_K: int = 4

    # OCR Engine
    OCR_ENGINE: str = "auto"  # "auto" | "pymupdf" | "tesseract"
    TESSERACT_CMD: str = ""

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
