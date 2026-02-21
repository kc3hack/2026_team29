"""Quest CRUD操作"""

from sqlalchemy.orm import Session

from app.models.enums import QuestCategory
from app.models.quest import Quest
from app.schemas.quest import QuestCreate


def get_quest(db: Session, quest_id: int) -> Quest | None:
    return db.query(Quest).filter(Quest.id == quest_id).first()


def list_quests(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    category: QuestCategory | None = None,
    difficulty: int | None = None,
) -> list[Quest]:
    query = db.query(Quest)
    if category is not None:
        query = query.filter(Quest.category == category.value)
    if difficulty is not None:
        query = query.filter(Quest.difficulty == difficulty)
    # ページネーション結果を安定させるため主キーで明示的にソート
    query = query.order_by(Quest.id.asc())
    return query.offset(skip).limit(limit).all()


def list_quests_by_category(db: Session, category: QuestCategory) -> list[Quest]:
    return db.query(Quest).filter(Quest.category == category.value).all()


def create_quest(db: Session, quest_in: QuestCreate) -> Quest:
    db_quest = Quest(
        title=quest_in.title,
        description=quest_in.description,
        difficulty=quest_in.difficulty,
        category=quest_in.category.value,
        is_generated=quest_in.is_generated,
    )
    db.add(db_quest)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(db_quest)
    return db_quest


def delete_quest(db: Session, quest_id: int) -> bool:
    """クエストを削除する。存在しない場合は False を返す。"""
    db_quest = db.query(Quest).filter(Quest.id == quest_id).first()
    if db_quest is None:
        return False
    db.delete(db_quest)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return True
