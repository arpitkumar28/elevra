from fastapi import APIRouter

from app.api.v1 import auth as legacy_auth_router
from app.api.v1.cache import router as cache_router
from app.api.v1.endpoints import auth as dev_auth_router
from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.exams import router as exams_router
from app.api.v1.health import router as health_router
from app.api.v1.opportunities import router as opportunities_router
from app.api.v1.profile import router as profile_router
from app.api.v1.content import router as content_router
from app.api.v1.tests import router as tests_router
from app.api.v1.account import router as account_router

router = APIRouter()
router.include_router(health_router)
router.include_router(legacy_auth_router.router)
router.include_router(dev_auth_router.router)
router.include_router(cache_router)
router.include_router(admin_router)
router.include_router(profile_router)
router.include_router(exams_router)
router.include_router(opportunities_router)
router.include_router(content_router)
router.include_router(tests_router)
router.include_router(account_router)
