"""SkillTree CRUD操作"""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.enums import SkillCategory
from app.models.skill_tree import SkillTree


def get_skill_tree_by_user_category(
    db: Session, user_id: int, category: SkillCategory
) -> SkillTree | None:
    return (
        db.query(SkillTree)
        .filter(SkillTree.user_id == user_id, SkillTree.category == category.value)
        .first()
    )


def initialize_skill_trees_for_user(db: Session, user_id: int) -> list[SkillTree]:
    """ユーザーに対して6カテゴリ全てのSkillTreeを初期化する。

    commit は呼び出し元（create_user）に委ねる。
    User + SkillTree を 1 トランザクションで確定させるため、
    ここでは session.add のみ行い commit / rollback は行わない。
    """
    trees = []
    for category in SkillCategory:
        tree = SkillTree(
            user_id=user_id,
            category=category.value,
            tree_data={},
        )
        db.add(tree)
        trees.append(tree)
    return trees


def get_skill_trees_by_user(db: Session, user_id: int) -> list[SkillTree]:
    """ユーザーの全スキルツリーを取得する。"""
    return db.query(SkillTree).filter(SkillTree.user_id == user_id).all()


def update_skill_tree(
    db: Session, user_id: int, category: SkillCategory, tree_data: dict[str, Any]
) -> SkillTree:
    db_tree = get_skill_tree_by_user_category(db, user_id, category)
    if db_tree is None:
        raise ValueError(
            f"SkillTree for user_id={user_id}, category={category.value} not found"
        )
    db_tree.tree_data = tree_data
    db_tree.generated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(db_tree)
    return db_tree
