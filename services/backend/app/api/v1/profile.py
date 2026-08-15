from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.schemas.auth import ProfileResponse, ProfileUpdate
from app.services.auth import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])


def _profile_for(user: User, db: Session) -> StudentProfile:
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if profile is None:
        profile = StudentProfile(user_id=user.id, display_name=user.name)
        db.add(profile)
        db.flush()
    return profile


@router.get("", response_model=ProfileResponse)
def get_profile(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    return _profile_for(current_user, db)


@router.patch("", response_model=ProfileResponse)
def update_profile(payload: ProfileUpdate, current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    profile = _profile_for(current_user, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile
