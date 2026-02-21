"""QuestProgress CRUD操作"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.enums import QuestStatus
from app.models.quest_progress import QuestProgress


def get_quest_progress(
    db: Session, user_id: int, quest_id: int
) -> QuestProgress | None:
    return (
        db.query(QuestProgress)
        .filter(QuestProgress.user_id == user_id, QuestProgress.quest_id == quest_id)
        .first()
    )


def get_quest_progress_by_user(db: Session, user_id: int) -> list[QuestProgress]:
    """ユーザーの全クエスト進捗を取得する。"""
    return db.query(QuestProgress).filter(QuestProgress.user_id == user_id).all()


def start_quest(db: Session, user_id: int, quest_id: int) -> QuestProgress:
    db_progress = QuestProgress(
        user_id=user_id,
        quest_id=quest_id,
        status=QuestStatus.IN_PROGRESS.value,
        started_at=datetime.now(timezone.utc),
    )
    db.add(db_progress)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise ValueError(
            f"QuestProgress for user_id={user_id} and quest_id={quest_id} already exists"
        ) from e
    except Exception:
        db.rollback()
        raise
    db.refresh(db_progress)
    return db_progress


def complete_quest(db: Session, user_id: int, quest_id: int) -> QuestProgress:
    db_progress = get_quest_progress(db, user_id, quest_id)
    if db_progress is None:
        raise ValueError(
            f"QuestProgress for user_id={user_id}, quest_id={quest_id} not found"
        )
    db_progress.status = QuestStatus.COMPLETED.value
    db_progress.completed_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(db_progress)
    return db_progress
