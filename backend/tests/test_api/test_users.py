"""User API エンドポイントテスト（Issue #51）"""

import pytest
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app


@pytest.fixture()
def client(db):
    """DB override を設定したテストクライアント。"""

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# POST /users
# ---------------------------------------------------------------------------


def test_create_user_success(client):
    res = client.post("/api/v1/users", json={"username": "testuser"})
    assert res.status_code == 201
    data = res.json()
    assert data["username"] == "testuser"
    assert data["level"] == 1
    assert data["exp"] == 0
    assert data["rank"] == 0
    assert "id" in data


def test_create_user_duplicate_username(client):
    client.post("/api/v1/users", json={"username": "duplicate"})
    res = client.post("/api/v1/users", json={"username": "duplicate"})
    assert res.status_code == 400


# ---------------------------------------------------------------------------
# GET /users/{user_id}
# ---------------------------------------------------------------------------


def test_get_user_success(client):
    user_id = client.post("/api/v1/users", json={"username": "getme"}).json()["id"]
    res = client.get(f"/api/v1/users/{user_id}")
    assert res.status_code == 200
    assert res.json()["username"] == "getme"


def test_get_user_not_found(client):
    res = client.get("/api/v1/users/9999")
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# PUT /users/{user_id}
# ---------------------------------------------------------------------------


def test_update_user_username(client):
    user_id = client.post("/api/v1/users", json={"username": "before"}).json()["id"]
    res = client.put(f"/api/v1/users/{user_id}", json={"username": "after"})
    assert res.status_code == 200
    assert res.json()["username"] == "after"


def test_update_user_not_found(client):
    res = client.put("/api/v1/users/9999", json={"username": "nobody"})
    assert res.status_code == 404


def test_update_user_duplicate_username(client):
    """既存ユーザー名に変更しようとすると 400"""
    client.post("/api/v1/users", json={"username": "existing"})
    user_id = client.post("/api/v1/users", json={"username": "target"}).json()["id"]
    res = client.put(f"/api/v1/users/{user_id}", json={"username": "existing"})
    assert res.status_code == 400


def test_update_user_null_username(client):
    """username: null は無視され、既存の username が維持される"""
    user_id = client.post("/api/v1/users", json={"username": "nulltest"}).json()["id"]
    res = client.put(f"/api/v1/users/{user_id}", json={"username": None})
    assert res.status_code == 200
    assert res.json()["username"] == "nulltest"


# ---------------------------------------------------------------------------
# DELETE /users/{user_id}
# ---------------------------------------------------------------------------


def test_delete_user_success(client):
    user_id = client.post("/api/v1/users", json={"username": "todelete"}).json()["id"]
    res = client.delete(f"/api/v1/users/{user_id}")
    assert res.status_code == 204
    assert client.get(f"/api/v1/users/{user_id}").status_code == 404


def test_delete_user_not_found(client):
    res = client.delete("/api/v1/users/9999")
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# GET /users/{user_id}/profile
# ---------------------------------------------------------------------------


def test_get_profile_not_found(client):
    user_id = client.post("/api/v1/users", json={"username": "noprofile"}).json()["id"]
    res = client.get(f"/api/v1/users/{user_id}/profile")
    assert res.status_code == 404


def test_get_profile_user_not_found(client):
    res = client.get("/api/v1/users/9999/profile")
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# PUT /users/{user_id}/profile (Upsert)
# ---------------------------------------------------------------------------


def test_upsert_profile_create(client):
    user_id = client.post("/api/v1/users", json={"username": "profuser"}).json()["id"]
    res = client.put(
        f"/api/v1/users/{user_id}/profile",
        json={"github_username": "octocat", "qiita_id": "octocat_qiita"},
    )
    assert res.status_code == 200
    assert res.json()["github_username"] == "octocat"
    assert res.json()["qiita_id"] == "octocat_qiita"


def test_upsert_profile_update(client):
    user_id = client.post("/api/v1/users", json={"username": "profupdate"}).json()["id"]
    client.put(f"/api/v1/users/{user_id}/profile", json={"github_username": "first"})
    res = client.put(
        f"/api/v1/users/{user_id}/profile", json={"github_username": "second"}
    )
    assert res.status_code == 200
    assert res.json()["github_username"] == "second"


def test_upsert_profile_user_not_found(client):
    res = client.put("/api/v1/users/9999/profile", json={"github_username": "x"})
    assert res.status_code == 404


def test_get_profile_after_upsert(client):
    user_id = client.post("/api/v1/users", json={"username": "profget"}).json()["id"]
    client.put(f"/api/v1/users/{user_id}/profile", json={"github_username": "gh"})
    res = client.get(f"/api/v1/users/{user_id}/profile")
    assert res.status_code == 200
    assert res.json()["github_username"] == "gh"


# ---------------------------------------------------------------------------
# GET /users/{user_id}/badges
# ---------------------------------------------------------------------------


def test_get_badges_empty(client):
    user_id = client.post("/api/v1/users", json={"username": "badger"}).json()["id"]
    res = client.get(f"/api/v1/users/{user_id}/badges")
    assert res.status_code == 200
    assert res.json() == []


def test_get_badges_user_not_found(client):
    res = client.get("/api/v1/users/9999/badges")
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# GET /users/{user_id}/skill-trees
# ---------------------------------------------------------------------------


def test_get_skill_trees_six_categories(client):
    user_id = client.post("/api/v1/users", json={"username": "treeman"}).json()["id"]
    res = client.get(f"/api/v1/users/{user_id}/skill-trees")
    assert res.status_code == 200
    assert len(res.json()) == 6


def test_get_skill_trees_user_not_found(client):
    res = client.get("/api/v1/users/9999/skill-trees")
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# GET /users/{user_id}/quest-progress
# ---------------------------------------------------------------------------


def test_get_quest_progress_empty(client):
    user_id = client.post("/api/v1/users", json={"username": "quester"}).json()["id"]
    res = client.get(f"/api/v1/users/{user_id}/quest-progress")
    assert res.status_code == 200
    assert res.json() == []


def test_get_quest_progress_user_not_found(client):
    res = client.get("/api/v1/users/9999/quest-progress")
    assert res.status_code == 404
