from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.db.session import check_database
from app.infrastructure.cache import check_redis
from app.schemas.health import HealthResponse, ReadinessResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="backend")


@router.get("/ready", response_model=ReadinessResponse)
def readiness():
    dependencies = {
        "postgresql": {"status": "ok" if check_database() else "unavailable"},
        "redis": {"status": "ok" if check_redis() else "unavailable"},
    }
    ready = all(dependency["status"] == "ok" for dependency in dependencies.values())
    payload = {
        "status": "ready" if ready else "degraded",
        "service": "backend",
        "dependencies": dependencies,
    }
    return JSONResponse(
        status_code=status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        content=payload,
    )
