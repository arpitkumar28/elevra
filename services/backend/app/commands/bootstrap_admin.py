"""One-time, interactive bootstrap for the first Elevra administrator.

Run after the database schema has been migrated:
    python -m app.commands.bootstrap_admin

The command is deliberately not exposed as an HTTP endpoint. It requires a
TTY, hides password input, refuses to overwrite or promote existing accounts,
and creates an administrator only when no administrator already exists.
"""

from __future__ import annotations

import getpass
import sys

from pydantic import ValidationError
from sqlalchemy import or_, text
from sqlalchemy.orm import Session

from app.core.config import settings, validate_security_settings
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.services.auth import hash_password


class AdminBootstrapError(RuntimeError):
    """Raised when the initial admin bootstrap preconditions are not met."""


def create_initial_admin(
    db: Session,
    *,
    name: str,
    email: str,
    password: str,
) -> User:
    """Create the first admin in the current transaction; never promote users."""
    try:
        payload = RegisterRequest(name=name.strip(), email=email.strip(), password=password)
    except ValidationError as exc:
        # Do not echo submitted values (especially the password) in CLI output.
        messages = "; ".join(error.get("msg", "invalid value") for error in exc.errors())
        raise AdminBootstrapError(f"Invalid administrator details: {messages}") from None

    if db.get_bind().dialect.name == "postgresql":
        # Serialize concurrent invocations so two operators cannot both pass
        # the no-admin check at the same time.
        db.execute(text("SELECT pg_advisory_xact_lock(714229301)"))

    existing_admin = (
        db.query(User)
        .filter(
            or_(
                User.is_admin.is_(True),
                User.role.in_(("admin", "super_admin")),
            )
        )
        .first()
    )
    if existing_admin is not None:
        raise AdminBootstrapError(
            "An administrator already exists. Bootstrap is allowed only once."
        )

    existing_user = (
        db.query(User)
        .filter(User.email.ilike(str(payload.email)))
        .first()
    )
    if existing_user is not None:
        raise AdminBootstrapError(
            "That email already belongs to an account. This command never promotes existing users."
        )

    admin = User(
        name=payload.name,
        email=str(payload.email),
        password_hash=hash_password(payload.password),
        is_admin=True,
        is_active=True,
        role="admin",
        email_verified=False,
    )
    db.add(admin)
    db.flush()
    return admin


def main() -> int:
    if not sys.stdin.isatty():
        print("Run this command from an interactive terminal; no credentials were read.")
        return 2

    try:
        validate_security_settings(settings)
    except RuntimeError as exc:
        print(f"Configuration check failed: {exc}")
        return 2

    if settings.environment in {"development", "test"}:
        print("Refusing to bootstrap an administrator in development/test mode.")
        return 2

    print("Create the first Elevra administrator")
    print("This command works only when no admin account exists.")
    name = input("Admin name: ").strip()
    email = input("Admin email: ").strip()
    password = getpass.getpass("Admin password (input hidden): ")
    confirmation = getpass.getpass("Confirm password: ")

    if password != confirmation:
        print("Passwords do not match. No account was created.")
        return 2

    try:
        with SessionLocal.begin() as db:
            admin = create_initial_admin(
                db,
                name=name,
                email=email,
                password=password,
            )
            created_id = admin.id
            created_email = admin.email
    except AdminBootstrapError as exc:
        print(str(exc))
        return 2
    except Exception:
        print("Administrator creation failed. Check database connectivity and migration state.")
        return 1

    print(f"Created administrator: {created_email} (id: {created_id})")
    print("Sign in through the Elevra Admin app. No password was printed or stored in logs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
