"""Authentication and authorization dependencies."""

from datetime import UTC, datetime
from typing import Annotated

from app.db.session import get_db
from app.core.config import settings
from app.infrastructure.security.jwt import decode_access_token
from app.models.user import User
from app.schemas.users import CurrentUser
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

bearer_scheme = HTTPBearer(auto_error=False)


def _user_permissions(role: str, *, is_admin: bool = False) -> list[str]:
    permissions: list[str] = []
    if is_admin or role == "admin":
        permissions.append("analytics:read")
    if role == "super_admin":
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
    if subject == "00000000-0000-4000-8000-000000000001":
        if settings.environment not in {"development", "test"}:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required")
        roles = payload.get("roles") or ["student"]
        permissions = payload.get("permissions") or []
        return CurrentUser(
            id=subject,
            email=str(payload.get("email", "student@example.com")),
            full_name=str(payload.get("name", "Elevra Student")),
            roles=[str(role) for role in roles],
            permissions=[str(permission) for permission in permissions],
        )

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
    if getattr(user, "is_admin", False):
        roles = ["admin"]
    permissions = _user_permissions(user.role, is_admin=getattr(user, "is_admin", False))

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
