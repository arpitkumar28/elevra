from fastapi import APIRouter

from app.infrastructure.cache import CacheClient

router = APIRouter(prefix="/cache", tags=["cache"])


@router.get("/health")
def cache_health() -> dict[str, bool]:
    client = CacheClient()
    return {"healthy": client.ping()}
