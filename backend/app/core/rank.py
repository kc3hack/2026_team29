"""ランク計算ロジック（product-spec 4.1 準拠）

ランク0-9の10段階（種子〜世界樹）。
経験値の閾値は暫定値。仕様確定後に調整する。
"""

from sqlalchemy.orm import Session

from app.models.user import User

# 暫定的な経験値閾値（ランク0〜9に対応）
# ランクn に到達するために必要な累積経験値
_RANK_THRESHOLDS = [
    0,      # 0: 種子
    100,    # 1: 苗木
    300,    # 2: 若木
    600,    # 3: 巨木
    1000,   # 4: 母樹
    1500,   # 5: 林
    2500,   # 6: 森
    4000,   # 7: 霊樹
    6000,   # 8: 古樹
    9000,   # 9: 世界樹
]


def calculate_rank(exp: int) -> int:
    """経験値からランク（0-9）を算出する。"""
    rank = 0
    for i, threshold in enumerate(_RANK_THRESHOLDS):
        if exp >= threshold:
            rank = i
        else:
            break
    return rank


def update_user_exp(db: Session, user_id: int, exp_gained: int) -> User:
    """経験値を加算し、ランクを再計算する。"""
    user = db.query(User).filter(User.id == user_id).first()
    user.exp += exp_gained
    user.rank = calculate_rank(user.exp)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(user)
    return user
