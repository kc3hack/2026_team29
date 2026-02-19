"""Badge CRUD操作"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.badge import Badge
from app.schemas.badge import BadgeCreate


def get_badges_by_user(db: Session, user_id: int) -> list[Badge]:
    return db.query(Badge).filter(Badge.user_id == user_id).all()


def award_badge(db: Session, badge_in: BadgeCreate) -> Badge:
    db_badge = Badge(
        user_id=badge_in.user_id,
        category=badge_in.category.value,
        tier=badge_in.tier,
    )
    db.add(db_badge)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise ValueError(
            f"Badge for user_id={badge_in.user_id}, category={badge_in.category}, tier={badge_in.tier} already exists"
        ) from e
    except Exception:
        db.rollback()
        raise
    db.refresh(db_badge)
    return db_badge
