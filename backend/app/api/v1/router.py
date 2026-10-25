from fastapi import APIRouter
from app.api.v1.analyses import router as analyses_router
from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as documents_router
from app.api.v1.explanations import router as explanations_router
from app.api.v1.prescriptions import router as prescriptions_router

api_v1_router = APIRouter()

# Include versioned sub-routers
api_v1_router.include_router(auth_router)
api_v1_router.include_router(documents_router)
api_v1_router.include_router(analyses_router)
api_v1_router.include_router(prescriptions_router)
api_v1_router.include_router(explanations_router)
