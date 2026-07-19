from app.api.v1.endpoints import admin, auth, opportunities, system
from fastapi import APIRouter

router = APIRouter()

router.include_router(system.router)
router.include_router(auth.router)
router.include_router(opportunities.router)
router.include_router(admin.router)
