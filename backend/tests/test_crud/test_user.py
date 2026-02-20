import pytest

from app.crud.skill_tree import get_skill_tree_by_user_category
from app.crud.user import (
    create_user,
    delete_user,
    get_user,
    get_user_by_username,
    update_user,
    update_user_rank,
)
from app.models.enums import SkillCategory
from app.schemas.user import UserCreate, UserUpdate


def test_create_user(db):
    user_in = UserCreate(username="REID")
    user = create_user(db, user_in)

    assert user.id is not None
    assert user.username == "REID"
    assert user.level == 1
    assert user.exp == 0


def test_create_user_initializes_skill_trees(db):
    """ユーザー作成時に6カテゴリのSkillTreeが自動生成される"""
    user_in = UserCreate(username="SKILL_TEST")
    user = create_user(db, user_in)

    # 全6カテゴリのSkillTreeが存在することを確認
    for category in SkillCategory:
        tree = get_skill_tree_by_user_category(db, user.id, category)
        assert tree is not None, f"SkillTree for category {category.value} should exist"
        assert tree.user_id == user.id
        assert tree.category == category.value
        assert tree.tree_data == {}


def test_get_user(db):
    user_in = UserCreate(username="TAKUMI")
    created = create_user(db, user_in)

    found = get_user(db, created.id)
    assert found is not None
    assert found.username == "TAKUMI"


def test_get_user_not_found(db):
    result = get_user(db, 999)
    assert result is None


def test_get_user_by_username(db):
    user_in = UserCreate(username="MAX")
    create_user(db, user_in)

    found = get_user_by_username(db, "MAX")
    assert found is not None
    assert found.username == "MAX"


def test_get_user_by_username_not_found(db):
    result = get_user_by_username(db, "nonexistent")
    assert result is None


# ---------------------------------------------------------------------------
# update_user
# ---------------------------------------------------------------------------


def test_update_user_username(db):
    user = create_user(db, UserCreate(username="BEFORE"))
    updated = update_user(db, user.id, UserUpdate(username="AFTER"))
    assert updated is not None
    assert updated.username == "AFTER"


def test_update_user_partial(db):
    """未指定フィールドは変更されない。"""
    user = create_user(db, UserCreate(username="PARTIAL"))
    updated = update_user(db, user.id, UserUpdate())
    assert updated is not None
    assert updated.username == "PARTIAL"


def test_update_user_not_found(db):
    result = update_user(db, 9999, UserUpdate(username="NOBODY"))
    assert result is None


# ---------------------------------------------------------------------------
# delete_user
# ---------------------------------------------------------------------------


def test_delete_user_success(db):
    user = create_user(db, UserCreate(username="TODELETE"))
    result = delete_user(db, user.id)
    assert result is True
    assert get_user(db, user.id) is None


def test_delete_user_not_found(db):
    result = delete_user(db, 9999)
    assert result is False


# ---------------------------------------------------------------------------
# update_user_rank (AI専用)
# ---------------------------------------------------------------------------


def test_update_user_rank(db):
    user = create_user(db, UserCreate(username="RANKUP"))
    assert user.rank == 0
    updated = update_user_rank(db, user.id, 4)
    assert updated is not None
    assert updated.rank == 4


def test_update_user_rank_not_found(db):
    result = update_user_rank(db, 9999, 4)
    assert result is None


def test_update_user_null_username_ignored(db):
    """username=None は exclude_none=True により無視される。"""
    user = create_user(db, UserCreate(username="BEFORE_NULL"))
    updated = update_user(db, user.id, UserUpdate(username=None))
    assert updated is not None
    assert updated.username == "BEFORE_NULL"


def test_update_user_rank_out_of_range(db):
    """rank が 0-9 範囲外は ValueError を raise する。"""
    user = create_user(db, UserCreate(username="RANKVALIDATE"))
    with pytest.raises(ValueError):
        update_user_rank(db, user.id, 10)
