from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.cache import router as cache_router
from app.api.v1.health import router as health_router
from app.api.v1.exams import router as exams_router
from app.api.v1.opportunities import router as opportunities_router

router = APIRouter()
router.include_router(health_router)
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(cache_router)
router.include_router(exams_router)
router.include_router(opportunities_router)
