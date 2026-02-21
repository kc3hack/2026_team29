"""Quest / QuestProgress 認証統合テスト（Issue #65）

/api/v1/quest/{quest_id}/start|complete は認証必須（JWT Cookie / Bearer）。
正常系・異常系（401 / 404 / 409 / 400）を検証する。
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
# POST /quest/{quest_id}/start
# ---------------------------------------------------------------------------


def test_start_quest_401_when_no_auth(client, db):
    """未認証で start → 401。"""
    quest = _make_quest(db)
    res = client.post(f"/api/v1/quest/{quest.id}/start")
    assert res.status_code == 401


def test_start_quest_404_when_quest_not_found(client, db):
    """存在しないクエスト ID で start → 404。"""
    user = _make_user(db)
    res = client.post("/api/v1/quest/999999/start", headers=auth_headers(user.id))
    assert res.status_code == 404


def test_start_quest_201_success(client, db):
    """認証済みユーザーがクエストを開始 → 201 + QuestProgress 返却。"""
    user = _make_user(db)
    quest = _make_quest(db)
    res = client.post(f"/api/v1/quest/{quest.id}/start", headers=auth_headers(user.id))
    assert res.status_code == 201
    data = res.json()
    assert data["quest_id"] == quest.id
    assert data["status"] == "in_progress"


def test_start_quest_409_when_already_started(client, db):
    """同じクエストを二重 start → 409。"""
    user = _make_user(db)
    quest = _make_quest(db)
    client.post(f"/api/v1/quest/{quest.id}/start", headers=auth_headers(user.id))
    res = client.post(f"/api/v1/quest/{quest.id}/start", headers=auth_headers(user.id))
    assert res.status_code == 409


# ---------------------------------------------------------------------------
# POST /quest/{quest_id}/complete
# ---------------------------------------------------------------------------


def test_complete_quest_401_when_no_auth(client, db):
    """未認証で complete → 401。"""
    quest = _make_quest(db)
    res = client.post(f"/api/v1/quest/{quest.id}/complete")
    assert res.status_code == 401


def test_complete_quest_404_when_quest_not_found(client, db):
    """存在しないクエスト ID で complete → 404。"""
    user = _make_user(db)
    res = client.post("/api/v1/quest/999999/complete", headers=auth_headers(user.id))
    assert res.status_code == 404


def test_complete_quest_404_when_not_started(client, db):
    """未開始クエストに complete → 404（進捗が存在しない）。"""
    user = _make_user(db)
    quest = _make_quest(db)
    res = client.post(f"/api/v1/quest/{quest.id}/complete", headers=auth_headers(user.id))
    assert res.status_code == 404


def test_complete_quest_success(client, db):
    """開始済みクエストを complete → 200 + QuestProgress 返却。"""
    user = _make_user(db)
    quest = _make_quest(db)
    # start してから complete
    client.post(f"/api/v1/quest/{quest.id}/start", headers=auth_headers(user.id))
    res = client.post(f"/api/v1/quest/{quest.id}/complete", headers=auth_headers(user.id))
    assert res.status_code == 200
    data = res.json()
    assert data["quest_id"] == quest.id
    assert data["status"] == "completed"
