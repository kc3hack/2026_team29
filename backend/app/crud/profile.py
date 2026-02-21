"""Profile CRUD操作"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileUpdate


def get_profile_by_user_id(db: Session, user_id: int) -> Profile | None:
    return db.query(Profile).filter(Profile.user_id == user_id).first()


def create_profile(
    db: Session, profile_in: ProfileCreate, commit: bool = True
) -> Profile:
    data = profile_in.model_dump()
    # HttpUrlをstrに変換
    if data.get("portfolio_url"):
        data["portfolio_url"] = str(data["portfolio_url"])
    db_profile = Profile(**data)
    db.add(db_profile)
    if commit:
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise ValueError(
                f"Profile for user_id={profile_in.user_id} already exists"
            ) from e
        except Exception:
            db.rollback()
            raise
        db.refresh(db_profile)
    else:
        try:
            db.flush()
        except IntegrityError as e:
            db.rollback()
            raise ValueError(
                f"Profile for user_id={profile_in.user_id} already exists"
            ) from e
    return db_profile


def update_profile(db: Session, profile_id: int, profile_in: ProfileUpdate) -> Profile:
    db_profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if db_profile is None:
        raise ValueError(f"Profile with id={profile_id} not found")
    update_data = profile_in.model_dump(exclude_unset=True)
    # HttpUrlをstrに変換
    if "portfolio_url" in update_data and update_data["portfolio_url"]:
        update_data["portfolio_url"] = str(update_data["portfolio_url"])
    for field, value in update_data.items():
        setattr(db_profile, field, value)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(db_profile)
    return db_profile
