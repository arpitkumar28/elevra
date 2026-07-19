"""Authentication and authorization dependencies."""

from typing import Annotated

from app.infrastructure.security.jwt import decode_access_token
from app.schemas.users import CurrentUser
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(bearer_scheme)],
) -> CurrentUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc

    return CurrentUser(
        id=str(payload["sub"]),
        email=str(payload.get("email", "student@example.com")),
        full_name=str(payload.get("name", "Elevra Student")),
        roles=list(payload.get("roles", ["student"])),
        permissions=list(payload.get("permissions", [])),
    )


def require_permission(permission: str):
    async def dependency(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        if permission not in user.permissions and "super_admin" not in user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return dependency
