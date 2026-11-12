from __future__ import annotations

import html
import json
import logging
from datetime import UTC, datetime, timedelta
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.account_token import AccountToken
from app.models.email_outbox import EmailOutbox
from app.models.user import User

logger = logging.getLogger("app.email")


class EmailProviderError(Exception):
    def __init__(self, code: str, *, retryable: bool) -> None:
        super().__init__(code)
        self.code = code
        self.retryable = retryable


def email_delivery_is_configured(config=None) -> bool:
    """Return true only when every secret and URL needed to send securely exists."""
    config = config or settings
    required = (
        config.resend_api_key,
        config.email_from,
        config.email_frontend_url,
        config.email_outbox_encryption_key,
    )
    if not all(value.strip() for value in required):
        return False
    try:
        parsed = urlparse(config.email_frontend_url)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            return False
        if config.environment not in {"development", "test"} and parsed.scheme != "https":
            return False
        if not 1 <= config.email_outbox_max_attempts <= 10:
            return False
        if not 1 <= config.email_provider_timeout_seconds <= 30:
            return False
        if config.email_outbox_lease_seconds <= config.email_provider_timeout_seconds:
            return False
        Fernet(config.email_outbox_encryption_key.encode("ascii"))
    except (ValueError, UnicodeEncodeError):
        return False
    return True


def _fernet() -> Fernet:
    if not email_delivery_is_configured():
        raise RuntimeError("account email delivery is not configured")
    return Fernet(settings.email_outbox_encryption_key.encode("ascii"))


def enqueue_account_email(
    db: Session,
    *,
    account_token: AccountToken,
    recipient_email: str,
    purpose: str,
    token_value: str,
) -> EmailOutbox | None:
    """Persist an encrypted one-time token for retry-safe provider delivery."""
    if not email_delivery_is_configured():
        return None
    if purpose not in {"password_reset", "email_verification"}:
        raise ValueError("unsupported account email purpose")

    record = EmailOutbox(
        account_token_id=account_token.id,
        recipient_email=recipient_email,
        purpose=purpose,
        encrypted_token=_fernet().encrypt(token_value.encode("utf-8")).decode("ascii"),
        status="pending",
        attempt_count=0,
        max_attempts=settings.email_outbox_max_attempts,
        next_attempt_at=datetime.now(UTC),
    )
    db.add(record)
    db.flush()
    return record


def _message_content(outbox: EmailOutbox, user: User, token_value: str) -> tuple[str, str, str]:
    page = "reset-password" if outbox.purpose == "password_reset" else "verify-email"
    action = "reset your Elevra password" if outbox.purpose == "password_reset" else "verify your email address"
    expires = "1 hour" if outbox.purpose == "password_reset" else "24 hours"
    link = (
        f"{settings.email_frontend_url.rstrip('/')}/{page}?"
        f"{urlencode({'token': token_value})}"
    )
    name = html.escape(user.name or "there")
    escaped_link = html.escape(link, quote=True)
    subject = "Reset your Elevra password" if outbox.purpose == "password_reset" else "Verify your Elevra email"
    text_body = (
        f"Hi {user.name or 'there'},\n\n"
        f"Use this link to {action}:\n{link}\n\n"
        f"This link expires in {expires}. If you did not request this, you can ignore this email."
    )
    html_body = (
        f"<p>Hi {name},</p><p>Use the link below to {action}.</p>"
        f'<p><a href="{escaped_link}">{html.escape(action.capitalize())}</a></p>'
        f"<p>This link expires in {expires}. If you did not request this, "
        "you can safely ignore this email.</p><p>— Elevra</p>"
    )
    return subject, text_body, html_body


def _send_with_resend(outbox: EmailOutbox, user: User, token_value: str) -> str:
    subject, text_body, html_body = _message_content(outbox, user, token_value)
    payload = json.dumps(
        {
            "from": settings.email_from,
            "to": [outbox.recipient_email],
            "subject": subject,
            "text": text_body,
            "html": html_body,
        }
    ).encode("utf-8")
    request = Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {settings.resend_api_key}",
            "Content-Type": "application/json",
            # A stable key prevents duplicate sends when a provider accepted a
            # request but the worker lost its response or database commit.
            "Idempotency-Key": f"elevra-auth-{outbox.id}",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=settings.email_provider_timeout_seconds) as response:
            result = json.loads(response.read().decode("utf-8"))
            message_id = result.get("id") if isinstance(result, dict) else None
            if not isinstance(message_id, str) or not message_id:
                raise EmailProviderError("resend_invalid_success_response", retryable=True)
            return message_id
    except HTTPError as exc:
        retryable = exc.code in {408, 409, 425, 429} or 500 <= exc.code <= 599
        raise EmailProviderError(f"resend_http_{exc.code}", retryable=retryable) from None
    except (URLError, TimeoutError, OSError):
        raise EmailProviderError("resend_network_error", retryable=True) from None
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise EmailProviderError("resend_invalid_success_response", retryable=True) from None


def _claim_outbox_item(db: Session, *, outbox_id: str | None = None) -> str | None:
    now = datetime.now(UTC)
    eligible = or_(
        and_(
            EmailOutbox.status.in_(("pending", "retry")),
            EmailOutbox.next_attempt_at <= now,
        ),
        and_(
            EmailOutbox.status == "processing",
            EmailOutbox.locked_until.is_not(None),
            EmailOutbox.locked_until <= now,
        ),
    )
    query = db.query(EmailOutbox).filter(eligible)
    if outbox_id is not None:
        query = query.filter(EmailOutbox.id == outbox_id)
    record = (
        query.order_by(EmailOutbox.created_at.asc(), EmailOutbox.id.asc())
        .with_for_update(skip_locked=True)
        .first()
    )
    if record is None:
        return None
    record.status = "processing"
    record.locked_until = now + timedelta(seconds=settings.email_outbox_lease_seconds)
    record.attempt_count += 1
    record.updated_at = now
    db.commit()
    return record.id


def process_outbox_item(db: Session, *, outbox_id: str | None = None) -> bool:
    """Claim and attempt one due message using the caller's SQLAlchemy session."""
    claimed_id = _claim_outbox_item(db, outbox_id=outbox_id)
    if claimed_id is None:
        return False

    record = db.get(EmailOutbox, claimed_id)
    account_token = db.get(AccountToken, record.account_token_id) if record else None
    user = db.get(User, account_token.user_id) if account_token else None
    now = datetime.now(UTC)

    def fail_permanently(code: str) -> None:
        record.status = "failed"
        record.last_error = code[:128]
        record.encrypted_token = None
        record.locked_until = None
        if account_token is not None and account_token.used_at is None:
            account_token.used_at = now
        record.updated_at = now
        db.commit()

    if record is None or account_token is None or user is None:
        if record is not None:
            fail_permanently("account_token_or_user_missing")
        return True

    token_expires_at = account_token.expires_at
    if token_expires_at.tzinfo is None:
        token_expires_at = token_expires_at.replace(tzinfo=UTC)
    if (
        account_token.used_at is not None
        or token_expires_at <= now
        or account_token.purpose != record.purpose
    ):
        fail_permanently("account_token_invalid_or_expired")
        return True

    try:
        token_value = _fernet().decrypt(record.encrypted_token.encode("ascii")).decode("utf-8")
        provider_message_id = _send_with_resend(record, user, token_value)
    except InvalidToken:
        fail_permanently("outbox_token_decryption_failed")
        return True
    except (AttributeError, UnicodeEncodeError, RuntimeError):
        fail_permanently("email_delivery_configuration_invalid")
        return True
    except EmailProviderError as exc:
        record.last_error = exc.code
        record.locked_until = None
        record.updated_at = now
        if exc.retryable and record.attempt_count < record.max_attempts:
            delay = min(30 * (2 ** max(record.attempt_count - 1, 0)), 900)
            record.status = "retry"
            record.next_attempt_at = now + timedelta(seconds=delay)
        else:
            record.status = "failed"
            record.encrypted_token = None
            if account_token.used_at is None:
                account_token.used_at = now
        db.commit()
        logger.warning(
            "account_email_delivery_failed outbox_id=%s code=%s retryable=%s attempt=%s",
            record.id,
            exc.code,
            exc.retryable,
            record.attempt_count,
        )
        return True
    except Exception:
        # Do not leak provider payloads, tokens, or recipient addresses to logs.
        record.last_error = "email_delivery_unexpected_error"
        record.locked_until = None
        record.updated_at = now
        if record.attempt_count < record.max_attempts:
            record.status = "retry"
            record.next_attempt_at = now + timedelta(
                seconds=min(30 * (2 ** max(record.attempt_count - 1, 0)), 900)
            )
        else:
            record.status = "failed"
            record.encrypted_token = None
            if account_token.used_at is None:
                account_token.used_at = now
        db.commit()
        logger.exception("account_email_delivery_unexpected_error outbox_id=%s", record.id)
        return True

    record.status = "sent"
    record.provider_message_id = provider_message_id[:255]
    record.sent_at = now
    record.last_error = None
    record.locked_until = None
    # Delete the encrypted one-time token once the provider accepted the mail.
    record.encrypted_token = None
    record.updated_at = now
    db.commit()
    logger.info(
        "account_email_delivery_accepted outbox_id=%s provider_message_id=%s",
        record.id,
        record.provider_message_id,
    )
    return True


def dispatch_email_item(outbox_id: str) -> None:
    """FastAPI background-task entry point; opens its own short-lived DB session."""
    db = SessionLocal()
    try:
        process_outbox_item(db, outbox_id=outbox_id)
    finally:
        db.close()


def process_due_emails(*, limit: int = 50) -> int:
    """Worker entry point for retry sweeps or a scheduled cron invocation."""
    processed = 0
    for _ in range(max(1, min(limit, 500))):
        db = SessionLocal()
        try:
            did_process = process_outbox_item(db)
        finally:
            db.close()
        if not did_process:
            break
        processed += 1
    return processed
