from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Body, Cookie, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.account_token import AccountToken
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RegisterRequest,
    TokenRequest,
    TokenResponse,
)
from app.schemas.users import CurrentUser
from app.services.auth import (
    create_account_token,
    hash_password,
    hash_token_for_storage,
    issue_token_pair,
    revoke_refresh_token,
    rotate_refresh_token,
    get_current_user as get_db_user,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])
REFRESH_COOKIE = "elevra_refresh"


def _set_refresh_cookie(response: Response, token: str) -> None:
    from app.core.config import settings

    response.set_cookie(
        key=REFRESH_COOKIE,
        value=token,
        httponly=True,
        secure=settings.environment not in {"development", "test"},
        samesite="lax",
        max_age=settings.refresh_token_ttl_seconds,
        path="/api/v1/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    from app.core.config import settings

    response.delete_cookie(
        key=REFRESH_COOKIE,
        httponly=True,
        secure=settings.environment not in {"development", "test"},
        samesite="lax",
        path="/api/v1/auth",
    )


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(RefreshTokenRequest):
    pass


@router.post("/register", response_model=TokenResponse)
def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already registered")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role="student",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    tokens = issue_token_pair(db, user, request=request)
    _set_refresh_cookie(response, str(tokens["refresh_token"]))
    return TokenResponse(
        access_token=str(tokens["access_token"]),
        refresh_token=str(tokens["refresh_token"]),
        token_type="bearer",
        expires_in=int(tokens["expires_in"]),
    )


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    tokens = issue_token_pair(db, user, request=request)
    _set_refresh_cookie(response, str(tokens["refresh_token"]))
    return TokenResponse(
        access_token=str(tokens["access_token"]),
        refresh_token=str(tokens["refresh_token"]),
        token_type="bearer",
        expires_in=int(tokens["expires_in"]),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    payload: RefreshTokenRequest | None = Body(default=None),
    cookie_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE)] = None,
) -> TokenResponse:
    refresh_token = payload.refresh_token if payload and payload.refresh_token else cookie_token
    if not refresh_token:
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="refresh token required")
    try:
        tokens = rotate_refresh_token(db, refresh_token, request=request)
    except ValueError as exc:
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed") from exc
    except HTTPException:
        _clear_refresh_cookie(response)
        raise
    _set_refresh_cookie(response, str(tokens["refresh_token"]))

    return TokenResponse(
        access_token=str(tokens["access_token"]),
        refresh_token=str(tokens["refresh_token"]),
        token_type="bearer",
        expires_in=int(tokens["expires_in"]),
    )


@router.post("/logout")
def logout(
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
    user: Annotated[User, Depends(get_db_user)],
    payload: LogoutRequest | None = Body(default=None),
    cookie_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE)] = None,
) -> dict[str, str]:
    refresh_token = payload.refresh_token if payload else cookie_token
    if refresh_token:
        revoke_refresh_token(db, refresh_token, user_id=str(user.id))
    _clear_refresh_cookie(response)
    return {"message": "logged out"}


@router.get("/me")
def me(user: Annotated[CurrentUser, Depends(get_current_user)]) -> dict[str, str]:
    return {
        "id": user.id,
        "email": str(user.email),
        "name": user.full_name,
        "role": user.roles[0] if user.roles else "student",
    }


@router.post("/password-reset/request")
def password_reset_request(payload: PasswordResetRequest, db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    user = db.query(User).filter(User.email == payload.email).first()
    if user is not None:
        create_account_token(db, user, "password_reset", expires_in_hours=1)
        db.commit()
    return {"message": "If the account exists, a password reset email has been sent."}


@router.post("/password-reset/confirm")
def password_reset_confirm(payload: PasswordResetConfirm, db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    token = db.query(AccountToken).filter(AccountToken.token_hash == hash_token_for_storage(payload.token)).first()
    if token is None or token.used_at is not None or token.expires_at <= datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid or expired token")
    user = db.get(User, token.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid or expired token")
    user.password_hash = hash_password(payload.password)
    token.used_at = datetime.now(UTC)
    db.commit()
    return {"message": "password reset successful"}


@router.post("/verify-email/request")
def verify_email_request(payload: PasswordResetRequest, db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    user = db.query(User).filter(User.email == payload.email).first()
    if user is not None:
        create_account_token(db, user, "email_verification", expires_in_hours=24)
        db.commit()
    return {"message": "If the account exists, a verification email has been sent."}


@router.post("/verify-email/confirm")
def verify_email_confirm(payload: TokenRequest, db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    token = db.query(AccountToken).filter(AccountToken.token_hash == hash_token_for_storage(payload.token)).first()
    if token is None or token.used_at is not None or token.expires_at <= datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid or expired token")
    user = db.get(User, token.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid or expired token")
    user.email_verified = True
    token.used_at = datetime.now(UTC)
    db.commit()
    return {"message": "email verified"}
