"""Authentication and authorization dependencies."""

from datetime import UTC, datetime
from typing import Annotated

from app.db.session import get_db
from app.infrastructure.security.jwt import decode_access_token
from app.models.user import User
from app.schemas.users import CurrentUser
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

bearer_scheme = HTTPBearer(auto_error=False)


def _user_permissions(role: str) -> list[str]:
    permissions: list[str] = []
    if role == "admin":
        permissions.append("analytics:read")
    elif role == "super_admin":
        permissions.extend(["analytics:read", "users:read", "opportunities:approve"])
    return permissions


async def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(bearer_scheme)],
) -> CurrentUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authentication required",
        )
    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
        ) from exc

    subject = str(payload.get("sub"))
    user = db.get(User, subject)
    if user is None or not getattr(user, "is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authentication required",
        )

    if getattr(user, "locked_until", None) and user.locked_until > datetime.now(UTC):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="account temporarily locked",
        )

    roles = [user.role]
    permissions = _user_permissions(user.role)

    return CurrentUser(
        id=str(user.id),
        email=str(user.email),
        full_name=str(user.name),
        roles=roles,
        permissions=permissions,
    )


def require_permission(permission: str):
    async def dependency(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        if permission not in user.permissions and "super_admin" not in user.roles and "admin" not in user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="admin access required",
            )
        return user

    return dependency
