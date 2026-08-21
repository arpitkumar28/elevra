from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated

import bcrypt
from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.infrastructure.security.jwt import create_access_token, create_refresh_token, decode_access_token, decode_refresh_token
from app.models.account_token import AccountToken
from app.models.refresh_token import RefreshToken
from app.models.user import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def hash_token_for_storage(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _as_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    """Resolve the user represented by the existing bearer access token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required")
    try:
        access_token = authorization.split(" ", 1)[1]
        payload = decode_access_token(access_token)
        subject = payload.get("sub")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token") from exc
    if not isinstance(subject, str):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    user = db.get(User, subject)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required")
    return user


def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.is_admin or current_user.role in {"admin", "super_admin"}:
        return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="admin access required")


def build_roles_and_permissions(user: User) -> tuple[list[str], list[str]]:
    roles = [user.role]
    permissions: list[str] = []
    if user.is_admin or user.role == "admin":
        roles = ["admin"]
        permissions.append("analytics:read")
    if user.role == "super_admin":
        roles = ["super_admin"]
        permissions.extend(["analytics:read", "users:read", "opportunities:approve"])
    return roles, permissions


def create_session_record(
    db: Session,
    user: User,
    *,
    refresh_token_value: str,
    request: Request | None = None,
    session_id: str | None = None,
) -> RefreshToken:
    token_hash = hash_token_for_storage(refresh_token_value)
    now = datetime.now(UTC)
    record = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        session_id=session_id or uuid.uuid4().hex,
        user_agent=(request.headers.get("user-agent") if request and request.headers else None)[:512] if request and request.headers.get("user-agent") else None,
        ip_address=(request.client.host if request and request.client else None),
        expires_at=now + timedelta(seconds=settings.refresh_token_ttl_seconds),
        last_used_at=now,
        updated_at=now,
    )
    db.add(record)
    db.flush()
    return record


def issue_token_pair(db: Session, user: User, *, request: Request | None = None) -> dict[str, str | int]:
    session_id = uuid.uuid4().hex
    access_token = create_access_token(
        str(user.id),
        {
            "email": user.email,
            "name": user.name,
            "roles": [user.role],
            "permissions": build_roles_and_permissions(user)[1],
            "sid": session_id,
        },
    )
    refresh_token_value = create_refresh_token(str(user.id), {"sid": session_id})
    create_session_record(db, user, refresh_token_value=refresh_token_value, request=request, session_id=session_id)
    db.commit()
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_value,
        "token_type": "bearer",
        "expires_in": settings.access_token_ttl_seconds,
    }


def revoke_refresh_token(db: Session, refresh_token_value: str, *, user_id: str | None = None) -> bool:
    token_hash = hash_token_for_storage(refresh_token_value)
    token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if token is None:
        return False
    if user_id is not None and token.user_id != user_id:
        return False
    if token.revoked_at is None:
        token.revoked_at = datetime.now(UTC)
        db.commit()
        return True
    return False


def rotate_refresh_token(db: Session, refresh_token_value: str, *, request: Request | None = None) -> dict[str, str | int]:
    token_payload = decode_refresh_token(refresh_token_value)
    subject = str(token_payload.get("sub"))
    session_id = str(token_payload.get("sid")) if token_payload.get("sid") is not None else None
    token_hash = hash_token_for_storage(refresh_token_value)
    refresh_record = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if refresh_record is None or refresh_record.user_id != subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="refresh token revoked or invalid")
    if session_id is not None and refresh_record.session_id and refresh_record.session_id != session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="refresh token revoked or invalid")
    if refresh_record.revoked_at or _as_utc(refresh_record.expires_at) <= datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="refresh token revoked or invalid")

    now = datetime.now(UTC)
    new_session_id = uuid.uuid4().hex
    new_refresh_value = create_refresh_token(subject, {"sid": new_session_id})
    refresh_record.revoked_at = now
    refresh_record.last_used_at = now
    refresh_record.updated_at = now
    replacement = create_session_record(
        db,
        db.get(User, subject),
        refresh_token_value=new_refresh_value,
        request=request,
        session_id=new_session_id,
    )
    replacement.revoked_at = now
    replacement.last_used_at = now
    replacement.updated_at = now
    refresh_record.replaced_by = replacement.id
    user = refresh_record.user
    access_token = create_access_token(
        subject,
        {
            "email": user.email,
            "name": user.name,
            "roles": [user.role],
            "permissions": build_roles_and_permissions(user)[1],
            "sid": new_session_id,
        },
    )
    db.commit()
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_value,
        "token_type": "bearer",
        "expires_in": settings.access_token_ttl_seconds,
    }


def create_account_token(db: Session, user: User, purpose: str, *, expires_in_hours: int = 1) -> AccountToken:
    value = uuid.uuid4().hex
    token = AccountToken(
        user_id=user.id,
        purpose=purpose,
        token_hash=hash_token_for_storage(value),
        expires_at=datetime.now(UTC) + timedelta(hours=expires_in_hours),
    )
    db.add(token)
    db.flush()
    return token


def validate_account_token(db: Session, user: User, purpose: str, token_value: str) -> AccountToken | None:
    token_hash = hash_token_for_storage(token_value)
    token = (
        db.query(AccountToken)
        .filter(AccountToken.user_id == user.id, AccountToken.purpose == purpose, AccountToken.token_hash == token_hash)
        .first()
    )
    if token is None or token.used_at is not None or token.expires_at <= datetime.now(UTC):
        return None
    return token

