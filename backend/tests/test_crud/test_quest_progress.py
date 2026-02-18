from app.crud.quest import create_quest
from app.crud.quest_progress import (
    complete_quest,
    get_quest_progress,
    start_quest,
)
from app.crud.user import create_user
from app.models.enums import QuestCategory, QuestStatus
from app.schemas.quest import QuestCreate
from app.schemas.user import UserCreate


def _create_user_and_quest(db):
    user = create_user(db, UserCreate(username="qp_user"))
    quest = create_quest(
        db,
        QuestCreate(
            title="Test Quest",
            description="desc",
            difficulty=1,
            category=QuestCategory.WEB,
            is_generated=False,
        ),
    )
    return user, quest


def test_start_quest(db):
    user, quest = _create_user_and_quest(db)
    progress = start_quest(db, user.id, quest.id)

    assert progress.user_id == user.id
    assert progress.quest_id == quest.id
    assert progress.status == QuestStatus.IN_PROGRESS
    assert progress.started_at is not None
    assert progress.completed_at is None


def test_complete_quest(db):
    user, quest = _create_user_and_quest(db)
    start_quest(db, user.id, quest.id)
    progress = complete_quest(db, user.id, quest.id)

    assert progress.status == QuestStatus.COMPLETED
    assert progress.completed_at is not None


def test_get_quest_progress(db):
    user, quest = _create_user_and_quest(db)
    start_quest(db, user.id, quest.id)

    found = get_quest_progress(db, user.id, quest.id)
    assert found is not None
    assert found.status == QuestStatus.IN_PROGRESS


def test_get_quest_progress_not_found(db):
    result = get_quest_progress(db, 999, 999)
    assert result is None
