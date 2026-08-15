"""JWT creation and validation helpers."""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt import InvalidTokenError

from app.core.config import settings

ALGORITHM = "HS256"


def _build_token(subject: str, token_type: str, ttl_seconds: int, claims: dict[str, Any] | None = None) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ttl_seconds)).timestamp()),
        "type": token_type,
        **(claims or {}),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def create_access_token(subject: str, claims: dict[str, Any] | None = None) -> str:
    return _build_token(subject, "access", settings.access_token_ttl_seconds, claims)


def create_refresh_token(subject: str, claims: dict[str, Any] | None = None) -> str:
    return _build_token(subject, "refresh", settings.refresh_token_ttl_seconds, claims)


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[ALGORITHM],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
    except InvalidTokenError as exc:
        raise ValueError("Invalid token") from exc
    if payload.get("type") != expected_type:
        raise ValueError("Invalid token type")
    return payload


def decode_access_token(token: str) -> dict[str, Any]:
    return decode_token(token, "access")


def decode_refresh_token(token: str) -> dict[str, Any]:
    return decode_token(token, "refresh")
