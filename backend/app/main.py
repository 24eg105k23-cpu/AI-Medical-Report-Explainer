from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.exceptions import AppError
from app.core.logging import get_logger
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.schemas.common import HealthStatus
from app.services.ocr_service import ocr_service
from app.services.rag_service import rag_service

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure DB tables exist and seed initial reference corpus
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    try:
        with SessionLocal() as db:
            rag_service.initialize_reference_corpus(db)
        logger.info("Reference corpus successfully initialized.")
    except Exception as e:
        logger.warning(f"Could not initialize reference corpus at startup: {e}")

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
def health_check():
    db_connected = False
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
            db_connected = True
    except Exception as e:
        logger.error(f"Health check DB ping failed: {e}")

    return HealthStatus(
        status="healthy" if db_connected else "degraded",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        version="1.0.0",
        database_connected=db_connected,
        ocr_engine_available=True,
        llm_provider=settings.LLM_PROVIDER,
    )


# Readiness check endpoint
@app.get(
    "/ready",
    tags=["System"],
    summary="Readiness check probe",
)
def ready_check():
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "not_ready", "error": str(e)})


# Mount API V1
app.include_router(api_v1_router, prefix=settings.API_V1_STR)
