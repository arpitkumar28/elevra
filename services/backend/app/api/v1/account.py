from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.opportunity import Opportunity, OpportunityStatus
from app.models.platform import Application, ApplicationEvent, Bookmark, Notification
from app.schemas.platform import ApplicationUpdate, ApplicationWrite, BookmarkWrite
from app.services.audit import record_audit
from app.services.auth import get_current_user

router = APIRouter(tags=["student"])


def _record(item):
    return {column.name: getattr(item, column.name) for column in item.__table__.columns}


def _next_event_timestamp(db: Session, application_id: str) -> datetime:
    """Return a strictly increasing timestamp for one application's event stream."""
    latest = (
        db.query(ApplicationEvent.created_at)
        .filter(ApplicationEvent.application_id == application_id)
        .order_by(ApplicationEvent.created_at.desc())
        .first()
    )
    now = datetime.now(UTC)
    if latest is None or latest[0] is None:
        return now
    previous = latest[0]
    if previous.tzinfo is None:
        previous = previous.replace(tzinfo=UTC)
    return max(now, previous + timedelta(microseconds=1))


@router.post("/bookmarks", status_code=status.HTTP_201_CREATED)
def create_bookmark(payload: BookmarkWrite, request: Request, db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    if payload.entity_type == "opportunity":
        opportunity = db.get(Opportunity, payload.entity_id)
        if opportunity is None or opportunity.status != OpportunityStatus.published:
            raise HTTPException(status_code=409, detail="Only currently published opportunities can be saved")
    bookmark = Bookmark(user_id=user.id, **payload.model_dump())
    db.add(bookmark)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="bookmark already exists")
    record_audit(
        db,
        action="BOOKMARK",
        entity="bookmark",
        entity_id=bookmark.id,
        actor_id=user.id,
        request=request,
        metadata={"entity_type": bookmark.entity_type, "entity_id": bookmark.entity_id},
    )
    db.commit()
    db.refresh(bookmark)
    return _record(bookmark)


@router.get("/bookmarks")
def list_bookmarks(db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    return [
        _record(item)
        for item in db.query(Bookmark).filter(Bookmark.user_id == user.id).order_by(Bookmark.created_at.desc()).all()
    ]


@router.delete("/bookmarks/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(bookmark_id: str, db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    item = db.query(Bookmark).filter(Bookmark.id == bookmark_id, Bookmark.user_id == user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="bookmark not found")
    db.delete(item)
    db.commit()


@router.post("/applications", status_code=status.HTTP_201_CREATED)
def create_application(
    payload: ApplicationWrite,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user=Depends(get_current_user),
):
    values = payload.model_dump(exclude_unset=True)
    opportunity_id = values.get("opportunity_id")

    if opportunity_id:
        # Serialize duplicate checks for this student/opportunity pair on
        # PostgreSQL to prevent concurrent requests creating duplicate rows.
        if db.get_bind().dialect.name == "postgresql":
            db.execute(
                text("SELECT pg_advisory_xact_lock(hashtext(:lock_key))"),
                {"lock_key": f"elevra-application:{user.id}:{opportunity_id}"},
            )
        opportunity = db.get(Opportunity, opportunity_id)
        if opportunity is None or opportunity.status != OpportunityStatus.published:
            raise HTTPException(
                status_code=409,
                detail="Only a currently published Elevra opportunity can be tracked",
            )
        if opportunity.deadline is not None and opportunity.deadline < datetime.now(UTC).date():
            raise HTTPException(status_code=409, detail="The application deadline has passed")
        existing = db.query(Application).filter(
            Application.user_id == user.id,
            Application.opportunity_id == opportunity.id,
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="This opportunity is already in your application tracker")

        # Do not trust client-submitted copies of public content.
        values.update({
            "title": opportunity.title,
            "organization": opportunity.organization,
            "external_url": opportunity.application_url,
        })
    elif not values.get("title"):
        raise HTTPException(status_code=422, detail="A title is required for a manually tracked application")

    values["status"] = "saved"
    item = Application(user_id=user.id, **values)
    db.add(item)
    db.flush()
    db.add(ApplicationEvent(
        application_id=item.id,
        user_id=user.id,
        previous_status=None,
        new_status="saved",
        note="Application tracking started",
        created_at=_next_event_timestamp(db, item.id),
    ))
    record_audit(db, action="APPLICATION", entity="application", entity_id=item.id, actor_id=user.id, request=request)
    db.commit()
    db.refresh(item)
    return _record(item)


@router.get("/applications")
def list_applications(db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    return [
        _record(item)
        for item in db.query(Application)
        .filter(Application.user_id == user.id)
        .order_by(Application.updated_at.desc())
        .all()
    ]


@router.patch("/applications/{application_id}")
def update_application(
    application_id: str,
    payload: ApplicationUpdate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user=Depends(get_current_user),
):
    item = (
        db.query(Application)
        .filter(Application.id == application_id, Application.user_id == user.id)
        .with_for_update()
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="application not found")

    values = payload.model_dump(exclude_unset=True)
    status_note = values.pop("status_note", None)
    next_status = values.get("status")

    if next_status and next_status != item.status:
        allowed = {
            "saved": {"applied", "withdrawn"},
            "applied": {"in_progress", "interview", "selected", "rejected", "withdrawn"},
            "in_progress": {"interview", "selected", "rejected", "withdrawn"},
            "interview": {"selected", "rejected", "withdrawn"},
            "selected": {"withdrawn"},
            "rejected": {"applied", "withdrawn"},
            "withdrawn": {"applied"},
        }
        if next_status not in allowed.get(item.status, set()):
            raise HTTPException(
                status_code=409,
                detail=f"Cannot move an application from {item.status} to {next_status}",
            )
        previous_status = item.status
        if next_status == "applied" and item.applied_at is None:
            item.applied_at = datetime.now(UTC)
        db.add(ApplicationEvent(
            application_id=item.id,
            user_id=user.id,
            previous_status=previous_status,
            new_status=next_status,
            note=status_note,
            created_at=_next_event_timestamp(db, item.id),
        ))

    for key, value in values.items():
        setattr(item, key, value)

    record_audit(
        db,
        action="UPDATE",
        entity="application",
        entity_id=item.id,
        actor_id=user.id,
        request=request,
        metadata={"status": next_status} if next_status else {},
    )
    db.commit()
    db.refresh(item)
    return _record(item)


@router.get("/applications/{application_id}/events")
def list_application_events(
    application_id: str,
    db: Annotated[Session, Depends(get_db)],
    user=Depends(get_current_user),
):
    item = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="application not found")
    events = db.query(ApplicationEvent).filter(
        ApplicationEvent.application_id == item.id,
        ApplicationEvent.user_id == user.id,
    ).order_by(ApplicationEvent.created_at.asc()).all()
    return [_record(event) for event in events]


@router.delete("/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: str, db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    item = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="application not found")
    db.delete(item)
    db.commit()


@router.get("/notifications")
def list_notifications(db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    return [
        _record(item)
        for item in db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .all()
    ]


@router.post("/notifications/{notification_id}/read")
def read_notification(notification_id: str, db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    item = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="notification not found")
    item.read_at = datetime.now(UTC)
    db.commit()
    return {"status": "read"}


@router.post("/notifications/read-all")
def read_all_notifications(db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    db.query(Notification).filter(
        Notification.user_id == user.id,
        Notification.read_at.is_(None),
    ).update({Notification.read_at: datetime.now(UTC)}, synchronize_session=False)
    db.commit()
    return {"status": "read"}
