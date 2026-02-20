"""GitHub OAuth 認証エンドポイントテスト (Issue #59, ADR 014)

テスト方針:
  GitHub API への HTTP 通信は unittest.mock でモックし、
  実ネットワーク接続なしにフロー全体を検証する。

カバレッジ:
  GET /auth/github/login        → GitHub 認可ページへのリダイレクト
  GET /auth/github/callback     → 新規登録 / 既存ログイン / エラー系
  GET /auth/logout              → Cookie クリア
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app
from tests.conftest import auth_headers, make_test_token


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, follow_redirects=False) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# モック用ヘルパー
# ---------------------------------------------------------------------------

FAKE_GITHUB_USER = {
    "id": 12345,
    "login": "testuser_gh",
    "name": "Test User",
    "email": "test@example.com",
}

FAKE_ACCESS_TOKEN = "ghs_fakegithubaccesstoken"


def _mock_httpx_client(token_ok=True, user_ok=True, github_user=None):
    """httpx.Client をモックして GitHub API 応答を偽装するコンテキストマネージャを返す。"""
    if github_user is None:
        github_user = FAKE_GITHUB_USER

    mock_client = MagicMock()

    # POST (token exchange)
    mock_token_resp = MagicMock()
    mock_token_resp.raise_for_status = MagicMock()
    if token_ok:
        mock_token_resp.json.return_value = {"access_token": FAKE_ACCESS_TOKEN}
    else:
        mock_token_resp.json.return_value = {"error": "bad_verification_code"}

    # GET (user info)
    mock_user_resp = MagicMock()
    mock_user_resp.raise_for_status = MagicMock()
    mock_user_resp.json.return_value = github_user

    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.post = MagicMock(return_value=mock_token_resp)
    mock_client.get = MagicMock(return_value=mock_user_resp)

    return mock_client


def _valid_state() -> str:
    """検証が通る署名済み state を返す。"""
    from app.api.endpoints.auth import _sign_state
    import secrets
    return _sign_state(secrets.token_urlsafe(24))


# ---------------------------------------------------------------------------
# GET /auth/github/login
# ---------------------------------------------------------------------------


def test_login_redirects_to_github(client):
    """GITHUB_CLIENT_ID が設定されていればGitHubへ302リダイレクト。"""
    with patch("app.api.endpoints.auth.settings") as mock_settings:
        mock_settings.GITHUB_CLIENT_ID = "fake_client_id"
        mock_settings.JWT_SECRET_KEY = "test-jwt-secret-key-for-testing-only"
        res = client.get("/api/v1/auth/github/login")

    assert res.status_code in (302, 307)  # RedirectResponse デフォルトは 307
    assert "github.com/login/oauth/authorize" in res.headers["location"]
    assert "client_id=fake_client_id" in res.headers["location"]
    assert "scope=read%3Auser" in res.headers["location"] or "scope=read:user" in res.headers["location"]
    assert "state=" in res.headers["location"]


def test_login_503_when_no_client_id(client):
    """GITHUB_CLIENT_ID 未設定なら 503。"""
    with patch("app.api.endpoints.auth.settings") as mock_settings:
        mock_settings.GITHUB_CLIENT_ID = ""
        res = client.get("/api/v1/auth/github/login")

    assert res.status_code == 503


# ---------------------------------------------------------------------------
# GET /auth/github/callback - 新規ユーザー登録
# ---------------------------------------------------------------------------


def test_callback_new_user_creates_user_and_sets_cookie(client):
    """初回ログイン: User + OAuthAccount が作成され、JWT Cookie が付与されてフロントへリダイレクト。"""
    state = _valid_state()
    mock_client = _mock_httpx_client()

    with patch("app.api.endpoints.auth.httpx.Client", return_value=mock_client):
        res = client.get(f"/api/v1/auth/github/callback?code=fake_code&state={state}")

    assert res.status_code == 302
    assert "access_token" in res.cookies
    # Cookie は httpOnly なので値は取得できないが存在を確認
    set_cookie_header = res.headers.get("set-cookie", "")
    assert "access_token=" in set_cookie_header
    assert "httponly" in set_cookie_header.lower()


def test_callback_new_user_username_collision(client):
    """GitHub のログイン名がすでに使われている場合は username に ID を付与。"""
    state = _valid_state()
    # 同じ username を先に登録
    client.post("/api/v1/users", json={"username": "testuser_gh"})

    mock_client = _mock_httpx_client()
    with patch("app.api.endpoints.auth.httpx.Client", return_value=mock_client):
        res = client.get(f"/api/v1/auth/github/callback?code=fake_code&state={state}")

    assert res.status_code == 302
    assert "access_token" in res.cookies


# ---------------------------------------------------------------------------
# GET /auth/github/callback - 既存ユーザーログイン
# ---------------------------------------------------------------------------


def test_callback_existing_user_updates_token(client):
    """2回目以降のログイン: 既存 User の OAuthAccount token が更新され Cookie が付与される。"""
    state = _valid_state()
    mock_client = _mock_httpx_client()

    # 1回目: 新規登録
    with patch("app.api.endpoints.auth.httpx.Client", return_value=mock_client):
        res1 = client.get(f"/api/v1/auth/github/callback?code=fake_code&state={state}")
    assert res1.status_code == 302

    # 2回目: 既存ユーザーとしてログイン
    state2 = _valid_state()
    mock_client2 = _mock_httpx_client()
    with patch("app.api.endpoints.auth.httpx.Client", return_value=mock_client2):
        res2 = client.get(f"/api/v1/auth/github/callback?code=fake_code2&state={state2}")

    assert res2.status_code == 302
    assert "access_token" in res2.cookies


# ---------------------------------------------------------------------------
# GET /auth/github/callback - エラー系
# ---------------------------------------------------------------------------


def test_callback_invalid_state_returns_400(client):
    """state が改ざんされていると 400。"""
    res = client.get("/api/v1/auth/github/callback?code=fake_code&state=invalid.state")
    assert res.status_code == 400


def test_callback_missing_state_returns_422(client):
    """state パラメータなしは 422 (FastAPI バリデーション)。"""
    res = client.get("/api/v1/auth/github/callback?code=fake_code")
    assert res.status_code == 422


def test_callback_github_token_exchange_fails(client):
    """GitHub がアクセストークンを返さない場合は 400。"""
    state = _valid_state()
    mock_client = _mock_httpx_client(token_ok=False)

    with patch("app.api.endpoints.auth.httpx.Client", return_value=mock_client):
        res = client.get(f"/api/v1/auth/github/callback?code=bad_code&state={state}")

    assert res.status_code == 400


# ---------------------------------------------------------------------------
# GET /auth/logout
# ---------------------------------------------------------------------------


def test_logout_clears_cookie(client):
    """ログアウトで Set-Cookie に max-age=0 または expires=past が含まれる。"""
    # まず Cookie をセット（認証済みにする）
    state = _valid_state()
    mock_client = _mock_httpx_client()
    with patch("app.api.endpoints.auth.httpx.Client", return_value=mock_client):
        client.get(f"/api/v1/auth/github/callback?code=fake_code&state={state}")

    res = client.get("/api/v1/auth/logout")
    assert res.status_code == 200
    assert res.json() == {"message": "ログアウトしました"}
    # Cookie が削除されている（max-age=0 または空値）
    set_cookie_header = res.headers.get("set-cookie", "")
    assert "access_token" in set_cookie_header
    assert "max-age=0" in set_cookie_header.lower() or 'access_token=""' in set_cookie_header


def test_logout_without_cookie_still_200(client):
    """Cookie なしでもログアウトは 200 を返す。"""
    res = client.get("/api/v1/auth/logout")
    assert res.status_code == 200
