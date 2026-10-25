from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.exceptions import AppError
from app.core.logging import get_logger
from app.db.session import get_db, verify_database_connection, verify_database_schema_current
from app.schemas.common import HealthStatus
from app.services.ocr_service import ocr_service

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.APP_ENV != "test":
        if len(settings.SECRET_KEY) < 32 or settings.SECRET_KEY.lower().startswith("replace-"):
            raise RuntimeError(
                "SECRET_KEY must be a private random value of at least 32 characters. "
                "Generate one locally and set it in backend/.env."
            )
        if settings.APP_ENV.lower() in {"production", "prod"} and settings.DEBUG:
            raise RuntimeError("DEBUG must be false when APP_ENV is production.")
        if not settings.DB_PASSWORD:
            raise RuntimeError(
                "DB_PASSWORD is not configured. Copy .env.example to .env, set a local "
                "application password, and run the SQL setup script."
            )
        mysql_version = verify_database_connection()
        logger.info(
            "Connected to MySQL Server %s; native vector search is not assumed or used. "
            "RAG retrieval mode: %s.",
            mysql_version,
            settings.RETRIEVAL_MODE,
        )
    logger.info(f"{settings.APP_NAME} started in {settings.APP_ENV} mode.")
    yield
    # Shutdown
    logger.info("Application shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "AI-Powered Medical Report Analysis and Prescription Understanding System.\n\n"
        "**EDUCATIONAL PROTOTYPE NOTICE**: This system is designed solely for educational "
        "and informational purposes. It does not replace professional medical judgment, "
        "diagnose diseases, or prescribe medication."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom domain exception handler
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "details": exc.details,
        },
    )


# Generic unhandled exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing request {request.url.path}: {exc}", exc_info=settings.DEBUG)
    msg = str(exc) if settings.DEBUG else "An unexpected internal server error occurred."
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": msg,
        },
    )


# Health check endpoint
@app.get(
    "/health",
    response_model=HealthStatus,
    tags=["System"],
    summary="Health check probe",
)
def health_check(db: Session = Depends(get_db)):
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception as e:
        logger.error(f"Health check DB ping failed: {e}")

    ocr_available = ocr_service.tesseract_available
    return HealthStatus(
        status="healthy" if db_connected and ocr_available else "degraded",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        version="1.0.0",
        database_connected=db_connected,
        ocr_engine_available=ocr_available,
        llm_provider=settings.LLM_PROVIDER,
    )


# Readiness check endpoint
@app.get(
    "/ready",
    tags=["System"],
    summary="Readiness check probe",
)
def ready_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        if not verify_database_schema_current(db.connection()):
            return JSONResponse(
                status_code=503,
                content={"status": "not_ready", "error": "Database migrations are not up to date."},
            )
        return {"status": "ready"}
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "error": "Database is unavailable or migrations are missing."},
        )


# Mount API V1
app.include_router(api_v1_router, prefix=settings.API_V1_STR)
