from app.crud.skill_tree import get_skill_tree_by_user_category
from app.crud.user import create_user, get_user, get_user_by_username
from app.models.enums import SkillCategory
from app.schemas.user import UserCreate


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
