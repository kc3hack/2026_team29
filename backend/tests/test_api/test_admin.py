"""管理API（/admin）のテスト

Note: APIキー認証のテストはE2Eテストで実施。
ここではビジネスロジックをテストする。
"""

from app.api.admin import admin_create_quest, admin_delete_quest, admin_update_quest, fix_user_ranks
from app.crud.quest import get_quest
from app.crud.user import create_user
from app.models.enums import QuestCategory
from app.schemas.quest import QuestCreate, QuestUpdate
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
    """削除後、DB からクエストが取得できなくなる。"""
    created = admin_create_quest(quest_in=_quest_create(), db=db, _=None)
    admin_delete_quest(quest_id=created.id, db=db, _=None)
    assert get_quest(db, created.id) is None


# ---------------------------------------------------------------------------
# Quest 更新
# ---------------------------------------------------------------------------


def test_admin_update_quest_partial(db):
    """指定フィールドのみ更新される。"""
    created = admin_create_quest(quest_in=_quest_create(title="Before", difficulty=1), db=db, _=None)
    result = admin_update_quest(
        quest_id=created.id,
        quest_in=QuestUpdate(title="After"),
        db=db,
        _=None,
    )
    assert result.title == "After"
    assert result.difficulty == 1  # 変更していないフィールドはそのまま


def test_admin_update_quest_description_markdown(db):
    """description（Markdown）を更新できる。"""
    created = admin_create_quest(quest_in=_quest_create(), db=db, _=None)
    new_md = "## 新しい手順\n### Step 1\n内容を変更する"
    result = admin_update_quest(
        quest_id=created.id,
        quest_in=QuestUpdate(description=new_md),
        db=db,
        _=None,
    )
    assert result.description == new_md


def test_admin_update_quest_not_found(db):
    """存在しない ID を更新すると 404 例外が上がる。"""
    import pytest
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        admin_update_quest(
            quest_id=9999,
            quest_in=QuestUpdate(title="Ghost"),
            db=db,
            _=None,
        )
    assert exc_info.value.status_code == 404


def test_quest_update_explicit_null_raises_validation_error():
    """明示的に null を送ると 422 相当の ValidationError が上がる。

    nullable=False な DB 列への None 代入（IntegrityError→500）を防ぐ。
    """
    import pytest
    from pydantic import ValidationError

    # title=None を明示的にセット → model_fields_set に入るため reject_explicit_null が発火
    with pytest.raises(ValidationError) as exc_info:
        QuestUpdate(title=None)
    assert "title" in str(exc_info.value)

    with pytest.raises(ValidationError):
        QuestUpdate(description=None)

    with pytest.raises(ValidationError):
        QuestUpdate(difficulty=None)

    with pytest.raises(ValidationError):
        QuestUpdate(category=None)
