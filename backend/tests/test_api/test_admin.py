"""管理API（/admin）のテスト

Note: APIキー認証のテストはE2Eテストで実施。
このファイルでは、ランク修正ロジックに加えてクエスト生成・保存など管理API全般の挙動をテストする。
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.admin import _steps_to_markdown, admin_app, fix_user_ranks
from app.crud.user import create_user
from app.db.session import get_db
from app.models.enums import QuestCategory
from app.schemas.user import UserCreate

TEST_ADMIN_KEY = "test-admin-key-for-testing-only"  # conftest.py の ADMIN_API_KEY と一致
ADMIN_HEADERS = {"X-Admin-Key": TEST_ADMIN_KEY}

_MOCK_LLM_RESULT = {
    "title": "テスト: React カウンターアプリ",
    "difficulty": "beginner",
    "estimated_time_minutes": 30,
    "learning_objectives": ["State の理解", "イベントハンドリング"],
    "steps": [
        {
            "step_number": 1,
            "title": "セットアップ",
            "description": "プロジェクトを作成する",
            "code_example": "npx create-react-app my-app",
            "checkpoints": ["起動確認"],
        },
        {
            "step_number": 2,
            "title": "カウンター実装",
            "description": "useState で状態管理",
            "code_example": "",
            "checkpoints": [],
        },
    ],
    "resources": ["https://react.dev/"],
}


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
# Quest 生成 & 保存エンドポイント (Issue #77)
# ---------------------------------------------------------------------------


def test_steps_to_markdown_unit():
    """_steps_to_markdown が期待通りの Markdown を生成する（ADR 012）。"""
    md = _steps_to_markdown(_MOCK_LLM_RESULT)

    assert "## 学習目標" in md
    assert "- State の理解" in md
    assert "## Step 1: セットアップ" in md
    assert "npx create-react-app my-app" in md
    assert "- 起動確認" in md
    assert "## Step 2: カウンター実装" in md
    assert "## 参考リソース" in md
    assert "https://react.dev/" in md


def test_admin_generate_quest_success(admin_client, db):
    """LLM 生成 → DB 保存が成功し 201 + Quest レスポンスが返る。"""
    with patch(
        "app.api.admin.generate_handson_quest",
        new=AsyncMock(return_value=_MOCK_LLM_RESULT),
    ):
        res = admin_client.post(
            "/quests/generate",
            json={
                "document_content": "React の基本を学ぶドキュメントです。コンポーネント、State、Props について説明します。",
                "user_rank": 2,
                "user_skills": "JavaScript",
                "category": "web",
            },
            headers=ADMIN_HEADERS,
        )

    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "テスト: React カウンターアプリ"
    assert data["difficulty"] == 2
    assert data["category"] == QuestCategory.WEB.value
    assert data["is_generated"] is True
    assert "## 学習目標" in data["description"]
    assert "id" in data


def test_admin_generate_quest_is_persisted(admin_client, db):
    """生成されたクエストが DB に実際に保存される。"""
    with patch(
        "app.api.admin.generate_handson_quest",
        new=AsyncMock(return_value=_MOCK_LLM_RESULT),
    ):
        res = admin_client.post(
            "/quests/generate",
            json={
                "document_content": "Python の基本を学ぶドキュメントです。変数、関数、クラスについて詳しく説明します。",
                "user_rank": 1,
                "user_skills": "",
                "category": "ai",
            },
            headers=ADMIN_HEADERS,
        )

    assert res.status_code == 201
    quest_id = res.json()["id"]

    from app.crud.quest import get_quest
    saved = get_quest(db, quest_id)
    assert saved is not None
    assert saved.is_generated is True
    assert saved.category == QuestCategory.AI.value


def test_admin_generate_quest_llm_failure_returns_502(admin_client):
    """LLM 呼び出しが例外を出した場合 502 を返す。"""
    with patch(
        "app.api.admin.generate_handson_quest",
        new=AsyncMock(side_effect=RuntimeError("LLM timeout")),
    ):
        res = admin_client.post(
            "/quests/generate",
            json={
                "document_content": "テスト用ドキュメントの内容です。学習内容について詳しく解説します。",
                "user_rank": 0,
                "user_skills": "",
                "category": "web",
            },
            headers=ADMIN_HEADERS,
        )

    assert res.status_code == 502
    assert "Quest generation failed" in res.json()["detail"]


def test_admin_generate_quest_missing_api_key_returns_401(admin_client):
    """X-Admin-Key ヘッダーがない場合 401 を返す。"""
    res = admin_client.post(
        "/quests/generate",
        json={
            "document_content": "テスト用ドキュメントの内容です。",
            "user_rank": 0,
            "user_skills": "",
            "category": "web",
        },
    )
    assert res.status_code == 401


def test_admin_generate_quest_wrong_api_key_returns_401(admin_client):
    """不正な X-Admin-Key の場合 401 を返す。"""
    res = admin_client.post(
        "/quests/generate",
        json={
            "document_content": "テスト用ドキュメントの内容です。",
            "user_rank": 0,
            "user_skills": "",
            "category": "web",
        },
        headers={"X-Admin-Key": "wrong-key"},
    )
    assert res.status_code == 401


def test_admin_generate_quest_invalid_category_returns_422(admin_client):
    """存在しない category を渡した場合 422 を返す。"""
    with patch(
        "app.api.admin.generate_handson_quest",
        new=AsyncMock(return_value=_MOCK_LLM_RESULT),
    ):
        res = admin_client.post(
            "/quests/generate",
            json={
                "document_content": "テスト用ドキュメントの内容です。",
                "user_rank": 0,
                "user_skills": "",
                "category": "invalid_category",
            },
            headers=ADMIN_HEADERS,
        )
    assert res.status_code == 422


def test_admin_generate_quest_invalid_rank_returns_422(admin_client):
    """user_rank が範囲外（10以上）の場合 422 を返す。"""
    res = admin_client.post(
        "/quests/generate",
        json={
            "document_content": "テスト用ドキュメントの内容です。",
            "user_rank": 10,
            "user_skills": "",
            "category": "web",
        },
        headers=ADMIN_HEADERS,
    )
    assert res.status_code == 422


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
