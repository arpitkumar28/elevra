from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.platform import Application, Bookmark, Notification
from app.schemas.platform import ApplicationUpdate, ApplicationWrite, BookmarkWrite
from app.services.audit import record_audit
from app.services.auth import get_current_user

router = APIRouter(tags=["student"])


def _record(item):
    return {column.name: getattr(item, column.name) for column in item.__table__.columns}


@router.post("/bookmarks", status_code=status.HTTP_201_CREATED)
def create_bookmark(payload: BookmarkWrite, request: Request, db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    bookmark = Bookmark(user_id=user.id, **payload.model_dump()); db.add(bookmark)
    try:
        db.flush()
    except IntegrityError:
        db.rollback(); raise HTTPException(status_code=409, detail="bookmark already exists")
    record_audit(db, action="BOOKMARK", entity="bookmark", entity_id=bookmark.id, actor_id=user.id, request=request, metadata={"entity_type": bookmark.entity_type, "entity_id": bookmark.entity_id}); db.commit(); db.refresh(bookmark); return _record(bookmark)


@router.get("/bookmarks")
def list_bookmarks(db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    return [_record(item) for item in db.query(Bookmark).filter(Bookmark.user_id == user.id).order_by(Bookmark.created_at.desc()).all()]


@router.delete("/bookmarks/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(bookmark_id: str, db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    item = db.query(Bookmark).filter(Bookmark.id == bookmark_id, Bookmark.user_id == user.id).first()
    if not item: raise HTTPException(status_code=404, detail="bookmark not found")
    db.delete(item); db.commit()


@router.post("/applications", status_code=status.HTTP_201_CREATED)
def create_application(payload: ApplicationWrite, request: Request, db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    item = Application(user_id=user.id, **payload.model_dump()); db.add(item); db.flush(); record_audit(db, action="APPLICATION", entity="application", entity_id=item.id, actor_id=user.id, request=request); db.commit(); db.refresh(item); return _record(item)


@router.get("/applications")
def list_applications(db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    return [_record(item) for item in db.query(Application).filter(Application.user_id == user.id).order_by(Application.updated_at.desc()).all()]


@router.patch("/applications/{application_id}")
def update_application(application_id: str, payload: ApplicationUpdate, request: Request, db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    item = db.query(Application).filter(Application.id == application_id, Application.user_id == user.id).first()
    if not item: raise HTTPException(status_code=404, detail="application not found")
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(item, key, value)
    record_audit(db, action="UPDATE", entity="application", entity_id=item.id, actor_id=user.id, request=request); db.commit(); db.refresh(item); return _record(item)


@router.delete("/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: str, db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    item = db.query(Application).filter(Application.id == application_id, Application.user_id == user.id).first()
    if not item: raise HTTPException(status_code=404, detail="application not found")
    db.delete(item); db.commit()


@router.get("/notifications")
def list_notifications(db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    return [_record(item) for item in db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.created_at.desc()).all()]


@router.post("/notifications/{notification_id}/read")
def read_notification(notification_id: str, db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    item = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user.id).first()
    if not item: raise HTTPException(status_code=404, detail="notification not found")
    item.read_at = datetime.now(UTC); db.commit(); return {"status": "read"}


@router.post("/notifications/read-all")
def read_all_notifications(db: Annotated[Session, Depends(get_db)], user=Depends(get_current_user)):
    db.query(Notification).filter(Notification.user_id == user.id, Notification.read_at.is_(None)).update({Notification.read_at: datetime.now(UTC)}, synchronize_session=False); db.commit(); return {"status": "read"}
