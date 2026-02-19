"""ランク計算ロジック（product-spec 4.1 準拠）

ランク0-9の10段階（種子〜世界樹）。
経験値の閾値はconfig.pyで管理。
"""

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User


def calculate_rank(exp: int) -> int:
    """経験値からランク（0-9）を算出する。"""
    rank = 0
    for i, threshold in enumerate(settings.RANK_THRESHOLDS):
        if exp >= threshold:
            rank = i
        else:
            break
    return rank


def update_user_exp(db: Session, user_id: int, exp_gained: int) -> User:
    """経験値を加算し、ランクを再計算する。"""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise ValueError(f"User with id={user_id} not found")
    user.exp += exp_gained
    user.rank = calculate_rank(user.exp)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(user)
    return user
