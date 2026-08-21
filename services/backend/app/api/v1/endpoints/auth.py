"""Authentication endpoints for web, mobile, and future public API clients."""

from typing import Annotated

from app.api.dependencies.auth import get_current_user
from app.infrastructure.security.jwt import create_access_token
from app.schemas.users import CurrentUser, TokenPair
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=CurrentUser)
async def me(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
    return user


@router.post("/dev-token", response_model=TokenPair, include_in_schema=False)
async def dev_token() -> TokenPair:
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
