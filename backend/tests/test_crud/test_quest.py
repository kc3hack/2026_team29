from app.crud.quest import create_quest, get_quest, list_quests, list_quests_by_category
from app.models.enums import QuestCategory
from app.schemas.quest import QuestCreate


def _make_quest(db, *, title="Quest", difficulty=1, category=QuestCategory.WEB):
    return create_quest(
        db,
        QuestCreate(
            title=title,
            description="## 概要\nテスト用クエスト",
            difficulty=difficulty,
            category=category,
            is_generated=False,
        ),
    )


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
        QuestCreate(
            title="Web1",
            description="d",
            difficulty=1,
            category=QuestCategory.WEB,
            is_generated=False,
        ),
    )
    create_quest(
        db,
        QuestCreate(
            title="Web2",
            description="d",
            difficulty=2,
            category=QuestCategory.WEB,
            is_generated=False,
        ),
    )
    create_quest(
        db,
        QuestCreate(
            title="AI1",
            description="d",
            difficulty=3,
            category=QuestCategory.AI,
            is_generated=False,
        ),
    )

    web_quests = list_quests_by_category(db, QuestCategory.WEB)
    assert len(web_quests) == 2

    ai_quests = list_quests_by_category(db, QuestCategory.AI)
    assert len(ai_quests) == 1


# ---------------------------------------------------------------------------
# list_quests
# ---------------------------------------------------------------------------


def test_list_quests_all(db):
    _make_quest(db, title="Q1", category=QuestCategory.WEB)
    _make_quest(db, title="Q2", category=QuestCategory.AI)
    assert len(list_quests(db)) == 2


def test_list_quests_filter_category(db):
    _make_quest(db, title="Web1", category=QuestCategory.WEB)
    _make_quest(db, title="Web2", category=QuestCategory.WEB)
    _make_quest(db, title="AI1", category=QuestCategory.AI)
    result = list_quests(db, category=QuestCategory.WEB)
    assert len(result) == 2
    assert all(q.category == QuestCategory.WEB for q in result)


def test_list_quests_filter_difficulty(db):
    _make_quest(db, title="Easy", difficulty=1)
    _make_quest(db, title="Hard", difficulty=5)
    result = list_quests(db, difficulty=1)
    assert len(result) == 1
    assert result[0].title == "Easy"


def test_list_quests_filter_combined(db):
    _make_quest(db, title="WebEasy", category=QuestCategory.WEB, difficulty=1)
    _make_quest(db, title="WebHard", category=QuestCategory.WEB, difficulty=5)
    _make_quest(db, title="AIEasy", category=QuestCategory.AI, difficulty=1)
    result = list_quests(db, category=QuestCategory.WEB, difficulty=1)
    assert len(result) == 1
    assert result[0].title == "WebEasy"


def test_list_quests_pagination(db):
    for i in range(5):
        _make_quest(db, title=f"Quest{i}")
    assert len(list_quests(db, skip=2, limit=2)) == 2


def test_list_quests_empty(db):
    assert list_quests(db) == []
