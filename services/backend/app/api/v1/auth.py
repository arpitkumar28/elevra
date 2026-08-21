from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.infrastructure.security.jwt import decode_refresh_token
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
from app.services.auth import (
    create_account_token,
    hash_password,
    hash_token_for_storage,
    issue_token_pair,
    revoke_refresh_token,
    rotate_refresh_token,
    validate_account_token,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(RefreshTokenRequest):
    pass


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
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

    tokens = issue_token_pair(db, user)
    return TokenResponse(
        access_token=str(tokens["access_token"]),
        refresh_token=str(tokens["refresh_token"]),
        token_type="bearer",
        expires_in=int(tokens["expires_in"]),
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    tokens = issue_token_pair(db, user)
    return TokenResponse(
        access_token=str(tokens["access_token"]),
        refresh_token=str(tokens["refresh_token"]),
        token_type="bearer",
        expires_in=int(tokens["expires_in"]),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshTokenRequest, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    try:
        tokens = rotate_refresh_token(db, payload.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed") from exc
    except HTTPException:
        raise

    return TokenResponse(
        access_token=str(tokens["access_token"]),
        refresh_token=str(tokens["refresh_token"]),
        token_type="bearer",
        expires_in=int(tokens["expires_in"]),
    )


@router.post("/logout")
def logout(
    payload: LogoutRequest,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
    user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    revoke_refresh_token(db, payload.refresh_token, user_id=str(user.id))
    return {"message": "logged out"}


@router.get("/me")
def me(user: Annotated[User, Depends(get_current_user)]) -> dict[str, str]:
    return {"id": str(user.id), "email": user.email, "name": user.name, "role": user.role}


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
