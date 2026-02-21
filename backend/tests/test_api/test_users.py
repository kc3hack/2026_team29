"""User API エンドポイントテスト（Issue #51, #61）

/users/me 系 → JWT Bearer ヘッダーまたは Cookie 必須（ADR 014 / ADR 015）
/users/{id} 系管理者向けエンドポイントは別途管理 API で扱う。
"""

import pytest
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app
from tests.conftest import (
    auth_headers,
    make_expired_token,
    make_tampered_token,
    make_test_token,
)


@pytest.fixture()
def client(db):
    """DB override を設定したテストクライアント。"""

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def create_user(client, username: str) -> dict:
    """POST /auth/register でユーザーを作成して dict を返すテストヘルパー。"""
    res = client.post(
        "/api/v1/auth/register",
        json={"username": username, "password": "testpass123"},
    )
    assert (
        res.status_code == 201
    ), f"Failed to create user: {res.status_code} {res.text}"
    data = res.json()
    return {"id": data["user_id"], "username": username}


# ---------------------------------------------------------------------------
# GET /users/me  （認証必須）
# ---------------------------------------------------------------------------


def test_get_me_success(client):
    user = create_user(client, "me_user")
    res = client.get("/api/v1/users/me", headers=auth_headers(user["id"]))
    assert res.status_code == 200
    assert res.json()["username"] == "me_user"


def test_get_me_unauthorized(client):
    res = client.get("/api/v1/users/me")
    assert res.status_code == 401


# ---------------------------------------------------------------------------
# PUT /users/me  （認証必須）
# ---------------------------------------------------------------------------


def test_update_me_username(client):
    user = create_user(client, "before")
    res = client.put(
        "/api/v1/users/me",
        json={"username": "after"},
        headers=auth_headers(user["id"]),
    )
    assert res.status_code == 200
    assert res.json()["username"] == "after"


def test_update_me_unauthorized(client):
    res = client.put("/api/v1/users/me", json={"username": "nobody"})
    assert res.status_code == 401


def test_update_me_duplicate_username(client):
    """既存ユーザー名に変更しようとすると 400"""
    create_user(client, "existing")
    user = create_user(client, "target")
    res = client.put(
        "/api/v1/users/me",
        json={"username": "existing"},
        headers=auth_headers(user["id"]),
    )
    assert res.status_code == 400


def test_update_me_null_username(client):
    """username: null は無視され、既存の username が維持される"""
    user = create_user(client, "nulltest")
    res = client.put(
        "/api/v1/users/me",
        json={"username": None},
        headers=auth_headers(user["id"]),
    )
    assert res.status_code == 200
    assert res.json()["username"] == "nulltest"


# ---------------------------------------------------------------------------
# DELETE /users/me  （認証必須）
# ---------------------------------------------------------------------------


def test_delete_me_success(client):
    user = create_user(client, "todelete")
    res = client.delete("/api/v1/users/me", headers=auth_headers(user["id"]))
    assert res.status_code == 204
    # 削除後は同トークンで /me にアクセスしても 401
    assert (
        client.get("/api/v1/users/me", headers=auth_headers(user["id"])).status_code
        == 401
    )


def test_delete_me_unauthorized(client):
    res = client.delete("/api/v1/users/me")
    assert res.status_code == 401


# ---------------------------------------------------------------------------
# PUT /users/me/profile  （認証必須・Upsert）
# ---------------------------------------------------------------------------


def test_upsert_profile_create(client):
    user = create_user(client, "profuser")
    res = client.put(
        "/api/v1/users/me/profile",
        json={"github_username": "octocat", "qiita_id": "octocat_qiita"},
        headers=auth_headers(user["id"]),
    )
    assert res.status_code == 200
    assert res.json()["github_username"] == "octocat"
    assert res.json()["qiita_id"] == "octocat_qiita"


def test_upsert_profile_update(client):
    user = create_user(client, "profupdate")
    client.put(
        "/api/v1/users/me/profile",
        json={"github_username": "first"},
        headers=auth_headers(user["id"]),
    )
    res = client.put(
        "/api/v1/users/me/profile",
        json={"github_username": "second"},
        headers=auth_headers(user["id"]),
    )
    assert res.status_code == 200
    assert res.json()["github_username"] == "second"


def test_upsert_profile_unauthorized(client):
    res = client.put("/api/v1/users/me/profile", json={"github_username": "x"})
    assert res.status_code == 401


def test_get_my_profile(client):
    user = create_user(client, "profget")
    client.put(
        "/api/v1/users/me/profile",
        json={"github_username": "gh"},
        headers=auth_headers(user["id"]),
    )
    res = client.get("/api/v1/users/me/profile", headers=auth_headers(user["id"]))
    assert res.status_code == 200
    assert res.json()["github_username"] == "gh"


# ---------------------------------------------------------------------------
# GET /users/me/badges  （認証必須）
# ---------------------------------------------------------------------------


def test_get_my_badges_empty(client):
    user = create_user(client, "badger")
    res = client.get("/api/v1/users/me/badges", headers=auth_headers(user["id"]))
    assert res.status_code == 200
    assert res.json() == []


# ---------------------------------------------------------------------------
# GET /users/me/skill-trees  （認証必須）
# ---------------------------------------------------------------------------


def test_get_my_skill_trees_six_categories(client):
    user = create_user(client, "treeman")
    res = client.get("/api/v1/users/me/skill-trees", headers=auth_headers(user["id"]))
    assert res.status_code == 200
    assert len(res.json()) == 6


# ---------------------------------------------------------------------------
# GET /users/me/quest-progress  （認証必須）
# ---------------------------------------------------------------------------


def test_get_my_quest_progress_empty(client):
    user = create_user(client, "quester")
    res = client.get(
        "/api/v1/users/me/quest-progress", headers=auth_headers(user["id"])
    )
    assert res.status_code == 200
    assert res.json() == []


# ---------------------------------------------------------------------------
# JWT 後保証テスト（ADR 014: トークン検証の堅牢性）
# ---------------------------------------------------------------------------


def test_get_me_expired_token_is_rejected(client):
    """期限切れ JWT は 401 を返すこと（Token Expiry 後保証）"""
    user = create_user(client, "expired_user")
    client.cookies.clear()  # register で付与した Cookie を確実に削除
    headers = {"Authorization": f"Bearer {make_expired_token(user['id'])}"}
    res = client.get("/api/v1/users/me", headers=headers)
    assert res.status_code == 401


def test_get_me_tampered_token_is_rejected(client):
    """署名改ざん JWT は 401 を返すこと（Signature Validation 後保証）"""
    user = create_user(client, "tampered_user")
    client.cookies.clear()  # register で付与した Cookie を確実に削除
    headers = {"Authorization": f"Bearer {make_tampered_token(user['id'])}"}
    res = client.get("/api/v1/users/me", headers=headers)
    assert res.status_code == 401


def test_get_me_with_cookie_auth(client):
    """httpOnly Cookie 経由の JWT 認証で /users/me にアクセスできること（Cookie 認証後保証）"""
    user = create_user(client, "cookie_user")
    token = make_test_token(user["id"])
    client.cookies.set("access_token", token)
    res = client.get("/api/v1/users/me")
    assert res.status_code == 200
    assert res.json()["username"] == "cookie_user"
