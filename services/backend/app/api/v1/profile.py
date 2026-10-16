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


@router.get("/preferences")
def get_preferences(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    profile = _profile_for(current_user, db)
    return {
        "exam_interests": profile.exam_interests,
        "opportunity_interests": profile.opportunity_interests,
        "preferred_locations": profile.preferred_locations,
        "remote_preference": profile.remote_preference,
        "career_interests": profile.career_interests,
        "target_roles": profile.target_roles,
        "notification_preferences": profile.notification_preferences,
    }


@router.patch("/preferences")
def update_preferences(payload: ProfileUpdate, current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    profile = _profile_for(current_user, db)
    allowed = {"exam_interests", "opportunity_interests", "preferred_locations", "remote_preference", "career_interests", "target_roles", "notification_preferences"}
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field in allowed:
            setattr(profile, field, value)
    db.commit()
    return get_preferences(current_user, db)
