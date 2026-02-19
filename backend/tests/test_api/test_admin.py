"""管理API（/admin）のテスト

Note: APIキー認証のテストはE2Eテストで実施。
ここではランク修正ロジックのみをテストする。
"""

from app.api.admin import fix_user_ranks
from app.crud.user import create_user
from app.schemas.user import UserCreate


def test_fix_user_ranks_logic(db):
    """ランク修正ロジックのテスト"""
    # 不整合なランクを持つユーザーを作成
    user1 = create_user(db, UserCreate(username="user1"))
    user1.exp = 150  # rank=1 になるべき
    user1.rank = 0  # 不整合
    db.commit()

    user2 = create_user(db, UserCreate(username="user2"))
    user2.exp = 1000  # rank=4 になるべき
    user2.rank = 2  # 不整合
    db.commit()

    # fix_user_ranksを直接呼び出し（認証スキップ）
    result = fix_user_ranks(db=db, _=None)

    assert result["fixed_count"] == 2
    assert result["total_users"] == 2

    # ランクが修正されたことを確認
    db.refresh(user1)
    db.refresh(user2)
    assert user1.rank == 1
    assert user2.rank == 4
