"""Safe, append-only audit recording for state-changing API operations."""

from fastapi import Request
from sqlalchemy.orm import Session

from app.models.platform import AuditLog

_SECRET_KEYS = {"password", "token", "jwt", "refresh_token", "database_url", "redis_url", "service_role_key"}


def record_audit(db: Session, *, action: str, entity: str, entity_id: str | None, actor_id: str | None, request: Request | None = None, metadata: dict | None = None) -> None:
    safe_metadata = {key: value for key, value in (metadata or {}).items() if key.lower() not in _SECRET_KEYS}
    db.add(AuditLog(
        action=action, entity=entity, entity_id=entity_id, actor_id=actor_id,
        request_id=getattr(getattr(request, "state", None), "request_id", None), metadata_json=safe_metadata,
    ))
