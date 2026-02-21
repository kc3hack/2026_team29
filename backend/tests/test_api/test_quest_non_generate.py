"""Quest API エンドポイントテスト（Issue #53）

ユーザー作成は HTTP 経由でなく crud.user を直接使用する。
（POST /users は Issue #51 でのみ実装、develop にはまだ未マージのため）
"""

import pytest
from fastapi.testclient import TestClient

from app.crud.quest import create_quest
from app.crud.user import create_user
from app.db.session import get_db
from app.main import app
from app.models.enums import QuestCategory
from app.schemas.quest import QuestCreate
from app.schemas.user import UserCreate
from tests.conftest import auth_headers


@pytest.fixture()
def client(db):
    """DB override を設定したテストクライアント。"""

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _make_quest(db, *, title="Test Quest", difficulty=1, category=QuestCategory.WEB):
    return create_quest(
        db,
        QuestCreate(
            title=title,
            description="## 概要\nテスト用クエスト\n\n## 手順\nStep 1: 完了する",
            difficulty=difficulty,
            category=category,
            is_generated=False,
        ),
    )


def _make_user(db, username="testuser"):
    return create_user(db, UserCreate(username=username))


# ---------------------------------------------------------------------------
# GET /quests
# ---------------------------------------------------------------------------


def test_list_quests_empty(client):
    res = client.get("/api/v1/quest")
    assert res.status_code == 200
    assert res.json() == []


def test_list_quests_returns_all(client, db):
    _make_quest(db, title="Q1", category=QuestCategory.WEB)
    _make_quest(db, title="Q2", category=QuestCategory.AI)
    res = client.get("/api/v1/quest")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_list_quests_filter_category(client, db):
    _make_quest(db, title="Web1", category=QuestCategory.WEB)
    _make_quest(db, title="Web2", category=QuestCategory.WEB)
    _make_quest(db, title="AI1", category=QuestCategory.AI)
    res = client.get("/api/v1/quest?category=web")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert all(q["category"] == "web" for q in data)


def test_list_quests_filter_difficulty(client, db):
    _make_quest(db, title="Easy", difficulty=1)
    _make_quest(db, title="Hard", difficulty=5)
    res = client.get("/api/v1/quest?difficulty=1")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["title"] == "Easy"


def test_list_quests_pagination(client, db):
    for i in range(5):
        _make_quest(db, title=f"Quest{i}")
    res = client.get("/api/v1/quest?skip=2&limit=2")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_list_quests_response_schema(client, db):
    """GET /api/v1/quest は QuestSummary を返す（description 除外）。"""
    _make_quest(db, title="Schema Check")
    data = client.get("/api/v1/quest").json()[0]
    assert "id" in data
    assert "title" in data
    assert "description" not in data  # ADR 012: 一覧では description を返さない
    assert "difficulty" in data
    assert "category" in data
    assert "is_generated" in data
    assert "created_at" in data


# ---------------------------------------------------------------------------
# GET /quests/{quest_id}
# ---------------------------------------------------------------------------


def test_get_quest_success(client, db):
    quest = _make_quest(db, title="Detail Quest")
    res = client.get(f"/api/v1/quest/{quest.id}")
    assert res.status_code == 200
    assert res.json()["title"] == "Detail Quest"


def test_get_quest_markdown_description(client, db):
    quest = _make_quest(db)
    res = client.get(f"/api/v1/quest/{quest.id}")
    assert res.status_code == 200
    assert "##" in res.json()["description"]


def test_get_quest_not_found(client):
    res = client.get("/api/v1/quest/9999")
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# POST /quests/{quest_id}/start
# ---------------------------------------------------------------------------


def test_start_quest_success(client, db):
    quest = _make_quest(db)
    user = _make_user(db)
    res = client.post(f"/api/v1/quest/{quest.id}/start", headers=auth_headers(user.id))
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "in_progress"
    assert data["started_at"] is not None
    assert data["completed_at"] is None


def test_start_quest_not_found(client, db):
    user = _make_user(db)
    res = client.post("/api/v1/quest/9999/start", headers=auth_headers(user.id))
    assert res.status_code == 404


def test_start_quest_already_started(client, db):
    quest = _make_quest(db)
    user = _make_user(db)
    client.post(f"/api/v1/quest/{quest.id}/start", headers=auth_headers(user.id))
    res = client.post(f"/api/v1/quest/{quest.id}/start", headers=auth_headers(user.id))
    assert res.status_code == 409


# ---------------------------------------------------------------------------
# POST /quest/{quest_id}/complete
# ---------------------------------------------------------------------------


def test_complete_quest_success(client, db):
    quest = _make_quest(db)
    user = _make_user(db)
    client.post(f"/api/v1/quest/{quest.id}/start", headers=auth_headers(user.id))
    res = client.post(f"/api/v1/quest/{quest.id}/complete", headers=auth_headers(user.id))
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "completed"
    assert data["completed_at"] is not None


def test_complete_quest_not_found(client, db):
    user = _make_user(db)
    res = client.post("/api/v1/quest/9999/complete", headers=auth_headers(user.id))
    assert res.status_code == 404


def test_complete_quest_not_started(client, db):
    quest = _make_quest(db)
    user = _make_user(db)
    res = client.post(f"/api/v1/quest/{quest.id}/complete", headers=auth_headers(user.id))
    assert res.status_code == 404


def test_complete_quest_already_completed(client, db):
    quest = _make_quest(db)
    user = _make_user(db)
    client.post(f"/api/v1/quest/{quest.id}/start", headers=auth_headers(user.id))
    client.post(f"/api/v1/quest/{quest.id}/complete", headers=auth_headers(user.id))
    res = client.post(f"/api/v1/quest/{quest.id}/complete", headers=auth_headers(user.id))
    assert res.status_code == 400
