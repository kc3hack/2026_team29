"""管理API（/admin）のテスト

Note: APIキー認証のテストはE2Eテストで実施。
ここではビジネスロジックをテストする。
"""

from app.api.admin import admin_create_quest, admin_delete_quest, admin_list_quests, fix_user_ranks
from app.crud.user import create_user
from app.models.enums import QuestCategory
from app.schemas.quest import QuestCreate
from app.schemas.user import UserCreate


# ---------------------------------------------------------------------------
# テストヘルパー
# ---------------------------------------------------------------------------


def _quest_create(
    title: str = "テストクエスト",
    difficulty: int = 1,
    category: QuestCategory = QuestCategory.WEB,
    description: str = "## テスト\nテスト説明",
) -> QuestCreate:
    return QuestCreate(title=title, description=description, difficulty=difficulty, category=category)


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


# ---------------------------------------------------------------------------
# Quest 一覧
# ---------------------------------------------------------------------------


def test_admin_list_quests_empty(db):
    """クエストが0件の場合、空リストを返す。"""
    result = admin_list_quests(skip=0, limit=50, db=db, _=None)
    assert result == []


def test_admin_list_quests_returns_created(db):
    """作成したクエストが一覧に含まれる。"""
    admin_create_quest(quest_in=_quest_create(title="A"), db=db, _=None)
    admin_create_quest(quest_in=_quest_create(title="B"), db=db, _=None)
    result = admin_list_quests(skip=0, limit=50, db=db, _=None)
    assert len(result) == 2


def test_admin_list_quests_filter_category(db):
    """category フィルタが機能する。"""
    admin_create_quest(quest_in=_quest_create(category=QuestCategory.WEB), db=db, _=None)
    admin_create_quest(quest_in=_quest_create(category=QuestCategory.AI), db=db, _=None)
    result = admin_list_quests(skip=0, limit=50, category=QuestCategory.WEB, db=db, _=None)
    assert len(result) == 1
    assert result[0].category == QuestCategory.WEB


def test_admin_list_quests_skip_limit(db):
    """skip/limit が正しく動作する。"""
    for i in range(5):
        admin_create_quest(quest_in=_quest_create(title=f"Q{i}"), db=db, _=None)
    result = admin_list_quests(skip=2, limit=2, db=db, _=None)
    assert len(result) == 2


# ---------------------------------------------------------------------------
# Quest 手動作成
# ---------------------------------------------------------------------------


def test_admin_create_quest_returns_quest(db):
    """作成したクエストが Quest スキーマで返る。"""
    quest_in = _quest_create(title="新クエスト", difficulty=3, category=QuestCategory.SECURITY)
    result = admin_create_quest(quest_in=quest_in, db=db, _=None)
    assert result.id is not None
    assert result.title == "新クエスト"
    assert result.difficulty == 3
    assert result.category == QuestCategory.SECURITY
    assert result.is_generated is False
    assert result.description == "## テスト\nテスト説明"


def test_admin_create_quest_is_generated_false_by_default(db):
    """is_generated のデフォルトは False。"""
    result = admin_create_quest(quest_in=_quest_create(), db=db, _=None)
    assert result.is_generated is False


# ---------------------------------------------------------------------------
# Quest 削除
# ---------------------------------------------------------------------------


def test_admin_delete_quest_success(db):
    """存在するクエストを削除すると 204 相当で正常終了する。"""
    created = admin_create_quest(quest_in=_quest_create(), db=db, _=None)
    # delete は None を返す（204 No Content）
    result = admin_delete_quest(quest_id=created.id, db=db, _=None)
    assert result is None


def test_admin_delete_quest_not_found(db):
    """存在しない ID を削除すると 404 例外が上がる。"""
    from fastapi import HTTPException
    import pytest

    with pytest.raises(HTTPException) as exc_info:
        admin_delete_quest(quest_id=9999, db=db, _=None)
    assert exc_info.value.status_code == 404


def test_admin_delete_quest_removes_from_list(db):
    """削除後、一覧から取得できなくなる。"""
    created = admin_create_quest(quest_in=_quest_create(), db=db, _=None)
    admin_delete_quest(quest_id=created.id, db=db, _=None)
    result = admin_list_quests(skip=0, limit=50, db=db, _=None)
    assert all(q.id != created.id for q in result)
