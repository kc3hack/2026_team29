"""Profile CRUD操作"""

from sqlalchemy.orm import Session

from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileUpdate


def get_profile_by_user_id(db: Session, user_id: int) -> Profile | None:
    return db.query(Profile).filter(Profile.user_id == user_id).first()


def create_profile(db: Session, profile_in: ProfileCreate) -> Profile:
    db_profile = Profile(**profile_in.model_dump())
    db.add(db_profile)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(db_profile)
    return db_profile


def update_profile(db: Session, profile_id: int, profile_in: ProfileUpdate) -> Profile:
    db_profile = db.query(Profile).filter(Profile.id == profile_id).first()
    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_profile, field, value)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(db_profile)
    return db_profile
