from app.crud.skill_tree import (
    get_skill_tree_by_user_category,
    initialize_skill_trees_for_user,
    update_skill_tree,
)
from app.crud.user import create_user
from app.models.enums import SkillCategory
from app.schemas.user import UserCreate


def test_initialize_skill_trees_for_user(db):
    """ユーザー作成時に6カテゴリ全てのSkillTreeが生成される"""
    user = create_user(db, UserCreate(username="skill_tree_user"))
    trees = initialize_skill_trees_for_user(db, user.id)

    assert len(trees) == 6
    categories = {t.category for t in trees}
    assert categories == {
        SkillCategory.WEB,
        SkillCategory.AI,
        SkillCategory.SECURITY,
        SkillCategory.INFRASTRUCTURE,
        SkillCategory.DESIGN,
        SkillCategory.GAME,
    }
    for tree in trees:
        assert tree.tree_data == {}
        assert tree.generated_at is None


def test_get_skill_tree_by_user_category(db):
    user = create_user(db, UserCreate(username="get_tree_user"))
    initialize_skill_trees_for_user(db, user.id)

    tree = get_skill_tree_by_user_category(db, user.id, SkillCategory.WEB)
    assert tree is not None
    assert tree.category == SkillCategory.WEB


def test_get_skill_tree_not_found(db):
    result = get_skill_tree_by_user_category(db, 999, SkillCategory.WEB)
    assert result is None


def test_update_skill_tree(db):
    user = create_user(db, UserCreate(username="update_tree_user"))
    initialize_skill_trees_for_user(db, user.id)

    tree_data = {
        "nodes": [
            {"id": "html", "name": "HTML", "level": 3},
            {"id": "css", "name": "CSS", "level": 2},
        ],
        "edges": [{"from": "html", "to": "css"}],
    }
    updated = update_skill_tree(db, user.id, SkillCategory.WEB, tree_data)

    assert updated.tree_data == tree_data
    assert updated.generated_at is not None
