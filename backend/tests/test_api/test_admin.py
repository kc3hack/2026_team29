"""管理API（/admin）のテスト

Note: APIキー認証のテストはE2Eテストで実施。
このファイルでは、ランク修正ロジックに加えてクエスト生成・保存など管理API全般の挙動をテストする。
"""

import pytest
from fastapi.testclient import TestClient

from app.api.admin import admin_app, fix_user_ranks
from app.crud.user import create_user
from app.db.session import get_db
from app.schemas.user import UserCreate

TEST_ADMIN_KEY = "test-admin-key-for-testing-only"  # conftest.py の ADMIN_API_KEY と一致
ADMIN_HEADERS = {"X-Admin-Key": TEST_ADMIN_KEY}

@pytest.fixture()
def admin_client(db):
    """admin_app に DB override を設定したテストクライアント。"""

    def override_get_db():
        yield db

    admin_app.dependency_overrides[get_db] = override_get_db
    with TestClient(admin_app) as c:
        yield c
    admin_app.dependency_overrides.clear()


def test_fix_user_ranks_logic(db):
    """ランク修正ロジックのテスト"""
    # 不整合なランクを持つユーザーを作成
    user1 = create_user(db, UserCreate(username="user1"))
    user1.exp = 150  # rank=1 になるべき
    user1.rank = 0  # 不整合
    db.commit()

    user2 = create_user(db, UserCreate(username="user2"))
    user2.exp = 1000  # rank=4 になるべき
    user2.rank = 2  # 不整合
    db.commit()

    # fix_user_ranksを直接呼び出し（認証スキップ）
    result = fix_user_ranks(db=db, _=None)

    assert result["fixed_count"] == 2
    assert result["total_users"] == 2

    # ランクが修正されたことを確認
    db.refresh(user1)
    db.refresh(user2)
    assert user1.rank == 1
    assert user2.rank == 4


# ---------------------------------------------------------------------------
# 手動クエスト作成 POST /admin/quests (Issue #77)
# ---------------------------------------------------------------------------

_MANUAL_QUEST_BODY = {
    "title": "手動テストクエスト",
    "description": "## 概要\n\nこれは手動で作成したクエストです。\n\n## 手順\n\n1. 完了する",
    "difficulty": 3,
    "category": "web",
    "is_generated": False,
}


def test_admin_create_quest_success(admin_client):
    """手動クエスト作成が 201 + Quest レスポンスを返す。"""
    res = admin_client.post("/quests", json=_MANUAL_QUEST_BODY, headers=ADMIN_HEADERS)

    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "手動テストクエスト"
    assert data["difficulty"] == 3
    assert data["category"] == "web"
    assert data["is_generated"] is False
    assert "id" in data


def test_admin_create_quest_unauthorized(admin_client):
    """認証なしで手動クエスト作成すると 401。"""
    res = admin_client.post("/quests", json=_MANUAL_QUEST_BODY)
    assert res.status_code == 401


def test_admin_create_quest_invalid_difficulty_returns_422(admin_client):
    """difficulty が範囲外（10以上）の場合 422 を返す。"""
    body = {**_MANUAL_QUEST_BODY, "difficulty": 10}
    res = admin_client.post("/quests", json=body, headers=ADMIN_HEADERS)
    assert res.status_code == 422


def test_admin_create_quest_invalid_category_returns_422(admin_client):
    """存在しない category の場合 422 を返す。"""
    body = {**_MANUAL_QUEST_BODY, "category": "unknown"}
    res = admin_client.post("/quests", json=body, headers=ADMIN_HEADERS)
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# クエスト一覧 GET /admin/quests (Issue #77)
# ---------------------------------------------------------------------------


def test_admin_list_quests_empty(admin_client):
    """DB にクエストがない場合は空リストを返す。"""
    res = admin_client.get("/quests", headers=ADMIN_HEADERS)
    assert res.status_code == 200
    assert res.json() == []


def test_admin_list_quests_returns_created(admin_client):
    """作成したクエストが一覧に含まれる。"""
    admin_client.post("/quests", json=_MANUAL_QUEST_BODY, headers=ADMIN_HEADERS)
    admin_client.post(
        "/quests",
        json={**_MANUAL_QUEST_BODY, "title": "クエスト2", "category": "ai"},
        headers=ADMIN_HEADERS,
    )

    res = admin_client.get("/quests", headers=ADMIN_HEADERS)
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_admin_list_quests_filter_by_category(admin_client):
    """category フィルターが機能する。"""
    admin_client.post("/quests", json=_MANUAL_QUEST_BODY, headers=ADMIN_HEADERS)
    admin_client.post(
        "/quests",
        json={**_MANUAL_QUEST_BODY, "title": "AIクエスト", "category": "ai"},
        headers=ADMIN_HEADERS,
    )

    res = admin_client.get("/quests?category=web", headers=ADMIN_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["category"] == "web"


def test_admin_list_quests_unauthorized(admin_client):
    """認証なしで一覧取得すると 401。"""
    res = admin_client.get("/quests")
    assert res.status_code == 401


def test_admin_list_quests_limit_over_max_returns_422(admin_client):
    """limit が上限（200）を超えると 422。"""
    res = admin_client.get("/quests?limit=201", headers=ADMIN_HEADERS)
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# クエスト削除 DELETE /admin/quests/{quest_id} (Issue #77)
# ---------------------------------------------------------------------------


def test_admin_delete_quest_success(admin_client):
    """存在するクエストを削除すると 204 を返す。"""
    create_res = admin_client.post("/quests", json=_MANUAL_QUEST_BODY, headers=ADMIN_HEADERS)
    quest_id = create_res.json()["id"]

    res = admin_client.delete(f"/quests/{quest_id}", headers=ADMIN_HEADERS)
    assert res.status_code == 204

    # 削除後は一覧から消えている
    list_res = admin_client.get("/quests", headers=ADMIN_HEADERS)
    ids = [q["id"] for q in list_res.json()]
    assert quest_id not in ids


def test_admin_delete_quest_not_found(admin_client):
    """存在しない quest_id を削除すると 404。"""
    res = admin_client.delete("/quests/99999", headers=ADMIN_HEADERS)
    assert res.status_code == 404


def test_admin_delete_quest_unauthorized(admin_client):
    """認証なしで削除すると 401。"""
    res = admin_client.delete("/quests/1")
    assert res.status_code == 401
