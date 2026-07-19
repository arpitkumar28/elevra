"""Operational endpoints for load balancers and monitors."""

from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "backend"}


@router.get("/readiness")
async def readiness_check() -> dict[str, str]:
    return {"status": "ready"}
