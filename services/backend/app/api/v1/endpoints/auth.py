"""Authentication endpoints for web, mobile, and future public API clients."""

from app.core.config import settings
from app.infrastructure.security.jwt import create_access_token
from app.schemas.users import TokenPair
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/dev-token", response_model=TokenPair, include_in_schema=False)
async def dev_token() -> TokenPair:
    if settings.environment not in {"development", "test"}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    user_id = "00000000-0000-4000-8000-000000000001"
    access_token = create_access_token(
        user_id,
        {
            "email": "student@example.com",
            "name": "Elevra Student",
            "roles": ["student", "super_admin"],
            "permissions": ["opportunities:approve", "users:read", "analytics:read"],
        },
    )
    return TokenPair(access_token=access_token, refresh_token="dev-refresh-token", expires_in=900)
