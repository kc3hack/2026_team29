from app.crud.quest import create_quest, get_quest, list_quests_by_category
from app.models.enums import QuestCategory
from app.schemas.quest import QuestCreate


def test_create_quest(db):
    quest_in = QuestCreate(
        title="Build a REST API",
        description="FastAPIでREST APIを構築する",
        difficulty=3,
        category=QuestCategory.WEB,
        is_generated=False,
    )
    quest = create_quest(db, quest_in)

    assert quest.id is not None
    assert quest.title == "Build a REST API"
    assert quest.difficulty == 3
    assert quest.category == QuestCategory.WEB
    assert quest.is_generated is False
    assert quest.created_at is not None


def test_get_quest(db):
    quest = create_quest(
        db,
        QuestCreate(
            title="ML basics",
            description="機械学習の基礎",
            difficulty=5,
            category=QuestCategory.AI,
            is_generated=True,
        ),
    )
    found = get_quest(db, quest.id)
    assert found is not None
    assert found.title == "ML basics"


def test_get_quest_not_found(db):
    result = get_quest(db, 999)
    assert result is None


def test_list_quests_by_category(db):
    create_quest(
        db,
        QuestCreate(title="Web1", description="d", difficulty=1, category=QuestCategory.WEB, is_generated=False),
    )
    create_quest(
        db,
        QuestCreate(title="Web2", description="d", difficulty=2, category=QuestCategory.WEB, is_generated=False),
    )
    create_quest(
        db,
        QuestCreate(title="AI1", description="d", difficulty=3, category=QuestCategory.AI, is_generated=False),
    )

    web_quests = list_quests_by_category(db, QuestCategory.WEB)
    assert len(web_quests) == 2

    ai_quests = list_quests_by_category(db, QuestCategory.AI)
    assert len(ai_quests) == 1
