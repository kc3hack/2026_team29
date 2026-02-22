"""GitHub OAuth 認証エンドポイントテスト (Issue #59, ADR 014)

テスト方針:
  GitHub API への HTTP 通信は unittest.mock でモックし、
  実ネットワーク接続なしにフロー全体を検証する。

カバレッジ:
  GET /auth/github/login        → GitHub 認可ページへのリダイレクト
  GET /auth/github/callback     → 新規登録 / 既存ログイン / エラー系
  POST /auth/logout             → Cookie クリア
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app


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
    """httpx.AsyncClient をモックして GitHub API 応答を偽装する async 対応モックを返す。"""
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

    # async with httpx.AsyncClient() as client: に対応
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(return_value=mock_token_resp)
    mock_client.get = AsyncMock(return_value=mock_user_resp)

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
        mock_settings.FRONTEND_URL = "http://localhost:3000"
        res = client.get("/api/v1/auth/github/login")

    assert res.status_code in (302, 307)  # RedirectResponse デフォルトは 307
    assert "github.com/login/oauth/authorize" in res.headers["location"]
    assert "client_id=fake_client_id" in res.headers["location"]
    assert (
        "scope=read%3Auser" in res.headers["location"]
        or "scope=read:user" in res.headers["location"]
    )
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
    client.cookies.set("oauth_state", state)
    mock_client = _mock_httpx_client()

    with patch("app.api.endpoints.auth.httpx.AsyncClient", return_value=mock_client):
        res = client.get(f"/api/v1/auth/github/callback?code=fake_code&state={state}")

    assert res.status_code == 302
    assert "access_token" in res.cookies
    # Cookie は httpOnly なので値は取得できないが存在を確認
    set_cookie_header = res.headers.get("set-cookie", "")
    assert "access_token=" in set_cookie_header
    assert "httponly" in set_cookie_header.lower()


def test_callback_new_user_creates_profile_with_github_username(client, db):
    """初回ログイン: User + OAuthAccount + Profile が同一トランザクションで作成され、
    Profile.github_username が GitHub login 名で設定される (Issue #71)。"""
    state = _valid_state()
    client.cookies.set("oauth_state", state)
    mock_client = _mock_httpx_client()

    with patch("app.api.endpoints.auth.httpx.AsyncClient", return_value=mock_client):
        res = client.get(f"/api/v1/auth/github/callback?code=fake_code&state={state}")

    assert res.status_code == 302

    # JWT デコードして user_id を取得
    import jwt as _jwt
    from app.core.config import settings as _settings

    token = res.cookies.get("access_token")
    assert token is not None
    payload = _jwt.decode(
        token, _settings.JWT_SECRET_KEY, algorithms=[_settings.JWT_ALGORITHM]
    )
    user_id = int(payload["sub"])

    # Profile が作成されていることを確認
    from app.crud.profile import get_profile_by_user_id

    profile = get_profile_by_user_id(db, user_id)
    assert profile is not None
    assert profile.github_username == FAKE_GITHUB_USER["login"]


def test_callback_new_user_username_collision(client, db):
    """GitHub のログイン名がすでに使われている場合は username に ID を付与。"""
    state = _valid_state()
    # 同じ username を先に登録（事前ユーザー作成の確認）
    pre_res = client.post(
        "/api/v1/auth/register",
        json={"username": "testuser_gh", "password": "testpass123"},
    )
    assert pre_res.status_code == 201

    client.cookies.set("oauth_state", state)
    mock_client = _mock_httpx_client()
    with patch("app.api.endpoints.auth.httpx.AsyncClient", return_value=mock_client):
        res = client.get(f"/api/v1/auth/github/callback?code=fake_code&state={state}")

    assert res.status_code == 302
    assert "access_token" in res.cookies
    # 衝突した場合 username は "{login}_{github_id}" 形式になることを検証
    token = res.cookies.get("access_token")
    assert token is not None
    # JWT デコードして user_id を取得し、DB上の username を確認
    import jwt as _jwt
    from app.core.config import settings as _settings

    payload = _jwt.decode(
        token, _settings.JWT_SECRET_KEY, algorithms=[_settings.JWT_ALGORITHM]
    )
    user_id = int(payload["sub"])
    from app.crud.user import get_user

    created_user = get_user(db, user_id)
    assert created_user is not None
    assert (
        created_user.username == f"{FAKE_GITHUB_USER['login']}_{FAKE_GITHUB_USER['id']}"
    )


# ---------------------------------------------------------------------------
# GET /auth/github/callback - 既存ユーザーログイン
# ---------------------------------------------------------------------------


def test_callback_existing_user_updates_token(client):
    """2回目以降のログイン: 既存 User の OAuthAccount token が更新され Cookie が付与される。"""
    state = _valid_state()
    mock_client = _mock_httpx_client()

    # 1回目: 新規登録
    client.cookies.set("oauth_state", state)
    with patch("app.api.endpoints.auth.httpx.AsyncClient", return_value=mock_client):
        res1 = client.get(f"/api/v1/auth/github/callback?code=fake_code&state={state}")
    assert res1.status_code == 302

    # 2回目: 既存ユーザーとしてログイン
    state2 = _valid_state()
    mock_client2 = _mock_httpx_client()
    client.cookies.set("oauth_state", state2)
    with patch("app.api.endpoints.auth.httpx.AsyncClient", return_value=mock_client2):
        res2 = client.get(
            f"/api/v1/auth/github/callback?code=fake_code2&state={state2}"
        )

    assert res2.status_code == 302
    assert "access_token" in res2.cookies


def test_callback_existing_user_without_profile_creates_profile(client, db):
    """既存ユーザーで Profile が欠損している場合、GitHub OAuth ログイン時に
    Profile を自動作成する（移行ケース対応: Issue #71）。"""
    # 既存ユーザーを Profile なしで準備（移行前データを模倣）
    from app.crud.user import create_user as db_create_user
    from app.crud.oauth_account import create_oauth_account
    from app.schemas.user import UserCreate
    from app.schemas.oauth_account import OAuthAccountCreate

    existing_user = db_create_user(
        db, UserCreate(username="legacy_user", password=None)
    )
    # OAuthAccount は存在するが Profile は存在しない状態
    create_oauth_account(
        db,
        OAuthAccountCreate(
            user_id=existing_user.id,
            provider="github",
            provider_user_id=str(FAKE_GITHUB_USER["id"]),
            access_token="old_token",
        ),
    )
    db.commit()

    # Profile が存在しないことを確認
    from app.crud.profile import get_profile_by_user_id

    assert get_profile_by_user_id(db, existing_user.id) is None

    # OAuth callback でログイン
    state = _valid_state()
    client.cookies.set("oauth_state", state)
    mock_client = _mock_httpx_client()
    with patch("app.api.endpoints.auth.httpx.AsyncClient", return_value=mock_client):
        res = client.get(f"/api/v1/auth/github/callback?code=fake_code&state={state}")

    assert res.status_code == 302

    # Profile が自動作成されたことを確認
    profile = get_profile_by_user_id(db, existing_user.id)
    assert profile is not None
    assert profile.github_username == FAKE_GITHUB_USER["login"]


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
    client.cookies.set("oauth_state", state)
    mock_client = _mock_httpx_client(token_ok=False)

    with patch("app.api.endpoints.auth.httpx.AsyncClient", return_value=mock_client):
        res = client.get(f"/api/v1/auth/github/callback?code=bad_code&state={state}")

    assert res.status_code == 400


# ---------------------------------------------------------------------------
# POST /auth/logout
# ---------------------------------------------------------------------------


def test_logout_clears_cookie(client):
    """ログアウトで Set-Cookie に max-age=0 または expires=past が含まれる。"""
    # まず Cookie をセット（認証済みにする）
    state = _valid_state()
    client.cookies.set("oauth_state", state)
    mock_client = _mock_httpx_client()
    with patch("app.api.endpoints.auth.httpx.AsyncClient", return_value=mock_client):
        client.get(f"/api/v1/auth/github/callback?code=fake_code&state={state}")

    res = client.post("/api/v1/auth/logout")
    assert res.status_code == 200
    assert res.json() == {"message": "ログアウトしました"}
    # Cookie が削除されている（max-age=0 または空値）
    set_cookie_header = res.headers.get("set-cookie", "")
    assert "access_token" in set_cookie_header
    assert (
        "max-age=0" in set_cookie_header.lower()
        or 'access_token=""' in set_cookie_header
    )


def test_logout_without_cookie_still_200(client):
    """Cookie なしでもログアウトは 200 を返す。"""
    res = client.post("/api/v1/auth/logout")
    assert res.status_code == 200


def test_logout_cookie_samesite_secure_for_https(client, monkeypatch):
    """HTTPS環境でログアウト時、Set-Cookieにsamesite=none; secureが設定される（Issue #122）。

    背景: Cookie削除は設定時と同じ属性（SameSite/Secure）が必須。
    本番環境（FRONTEND_URL=https://...）で確実に削除されることを担保する。
    """
    # FRONTEND_URLをHTTPSに設定
    monkeypatch.setattr("app.core.config.settings.FRONTEND_URL", "https://example.com")

    # まずCookieをセット（認証済みにする）
    state = _valid_state()
    client.cookies.set("oauth_state", state)
    mock_client = _mock_httpx_client()
    with patch("app.api.endpoints.auth.httpx.AsyncClient", return_value=mock_client):
        client.get(f"/api/v1/auth/github/callback?code=fake_code&state={state}")

    # ログアウト
    res = client.post("/api/v1/auth/logout")
    assert res.status_code == 200

    # Set-Cookieヘッダーを取得（access_token のみ削除される）
    set_cookie_headers = res.headers.get_list("set-cookie")
    assert len(set_cookie_headers) >= 1, "access_token の Cookie削除が必要"

    # access_tokenのSet-Cookieヘッダーを特定
    access_token_header = next(
        (h for h in set_cookie_headers if "access_token" in h), None
    )
    assert (
        access_token_header is not None
    ), "access_token の Cookie削除ヘッダーが見つからない"

    # HTTPS環境では samesite=none と secure が設定されることを確認
    access_token_header_lower = access_token_header.lower()
    assert (
        "samesite=none" in access_token_header_lower
    ), "HTTPS環境では samesite=none が必要（Cookie削除時も設定時と同じ属性が必須）"
    assert (
        "secure" in access_token_header_lower
    ), "HTTPS環境では secure が必要（Cookie削除時も設定時と同じ属性が必須）"

    # Cookieが削除されていることも確認（max-age=0）
    assert "max-age=0" in access_token_header_lower, "Cookie削除には max-age=0 が必要"


# ---------------------------------------------------------------------------
# GET /auth/github/callback - ネットワークエラー系 (T-1, T-2)
# ---------------------------------------------------------------------------


def test_callback_token_exchange_network_error(client):
    """HTTPネットワークエラーでトークン交換が失敗した場合は 502。"""
    state = _valid_state()
    client.cookies.set("oauth_state", state)

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(side_effect=httpx.HTTPError("connection error"))

    with patch("app.api.endpoints.auth.httpx.AsyncClient", return_value=mock_client):
        res = client.get(f"/api/v1/auth/github/callback?code=fake_code&state={state}")

    assert res.status_code == 502


def test_callback_user_info_network_error(client):
    """トークン取得成功後、GitHub ユーザー情報取得で HTTP エラーが発生した場合は 502。"""
    state = _valid_state()
    client.cookies.set("oauth_state", state)

    # 1 回目: token exchange 成功
    mock_token_client = MagicMock()
    mock_token_resp = MagicMock()
    mock_token_resp.raise_for_status = MagicMock()
    mock_token_resp.json.return_value = {"access_token": "ghs_fake_token"}
    mock_token_client.__aenter__ = AsyncMock(return_value=mock_token_client)
    mock_token_client.__aexit__ = AsyncMock(return_value=False)
    mock_token_client.post = AsyncMock(return_value=mock_token_resp)

    # 2 回目: user info で失敗
    mock_user_client = MagicMock()
    mock_user_client.__aenter__ = AsyncMock(return_value=mock_user_client)
    mock_user_client.__aexit__ = AsyncMock(return_value=False)
    mock_user_client.get = AsyncMock(side_effect=httpx.HTTPError("user info error"))

    with patch(
        "app.api.endpoints.auth.httpx.AsyncClient",
        side_effect=[mock_token_client, mock_user_client],
    ):
        res = client.get(f"/api/v1/auth/github/callback?code=fake_code&state={state}")

    assert res.status_code == 502


def test_callback_token_exchange_http_status_error(client):
    """GitHub サーバーが 4xx/5xx を返した場合 (raise_for_status) も 502 を返す。

    httpx.HTTPStatusError は httpx.HTTPError のサブクラスなので
    except ブロックで正しくキャッチされることを確認する。
    """
    state = _valid_state()
    client.cookies.set("oauth_state", state)

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
        "503 Service Unavailable", request=MagicMock(), response=MagicMock()
    )
    mock_client.post = AsyncMock(return_value=mock_resp)

    with patch("app.api.endpoints.auth.httpx.AsyncClient", return_value=mock_client):
        res = client.get(f"/api/v1/auth/github/callback?code=fake_code&state={state}")

    assert res.status_code == 502


# ---------------------------------------------------------------------------
# GET /auth/github/callback - リダイレクト先検証 (T-3)
# ---------------------------------------------------------------------------


def test_callback_redirect_location_is_frontend_url(client):
    """コールバック成功時のリダイレクト先が settings.FRONTEND_URL/dashboard になっている。"""
    from app.core.config import settings

    state = _valid_state()
    client.cookies.set("oauth_state", state)
    mock_client = _mock_httpx_client()
    with patch("app.api.endpoints.auth.httpx.AsyncClient", return_value=mock_client):
        res = client.get(f"/api/v1/auth/github/callback?code=fake_code&state={state}")

    assert res.status_code == 302
    assert res.headers["location"] == f"{settings.FRONTEND_URL}/dashboard"


# ---------------------------------------------------------------------------
# POST /auth/register  +  POST /auth/login  (Spec 2.1: 登録と認証の分離)
# ---------------------------------------------------------------------------


def test_register_creates_account_and_sets_cookie(client):
    """新規登録: username + password → 201 + JWT httpOnly Cookie 付与。"""
    res = client.post(
        "/api/v1/auth/register",
        json={"username": "brand_new_user", "password": "pass1234"},
    )

    assert res.status_code == 201
    assert res.json().get("user_id") is not None
    set_cookie_header = res.headers.get("set-cookie", "")
    assert "access_token=" in set_cookie_header
    assert "httponly" in set_cookie_header.lower()


def test_register_duplicate_username_returns_409(client):
    """同一 username の再登録 → 409 Conflict。"""
    client.post(
        "/api/v1/auth/register", json={"username": "dup_user", "password": "pass1234"}
    )
    res = client.post(
        "/api/v1/auth/register", json={"username": "dup_user", "password": "pass1234"}
    )
    assert res.status_code == 409


def test_login_unknown_user_returns_401(client):
    """存在しない username でログイン → 401（ユーザー列挙防止）。"""
    res = client.post(
        "/api/v1/auth/login", json={"username": "nobody", "password": "pass1234"}
    )
    assert res.status_code == 401


def test_login_existing_user_correct_password(client):
    """登録済みユーザーが正しいパスワードでログイン → 200。"""
    client.post(
        "/api/v1/auth/register", json={"username": "pw_user", "password": "correct_pw"}
    )

    res = client.post(
        "/api/v1/auth/login", json={"username": "pw_user", "password": "correct_pw"}
    )
    assert res.status_code == 200
    assert "access_token=" in res.headers.get("set-cookie", "")


def test_login_existing_user_wrong_password(client):
    """登録済みユーザーが誤ったパスワードを入力 → 401。"""
    client.post(
        "/api/v1/auth/register", json={"username": "pw_user2", "password": "correct_pw"}
    )

    res = client.post(
        "/api/v1/auth/login", json={"username": "pw_user2", "password": "wrong_pw"}
    )
    assert res.status_code == 401


def test_login_github_oauth_user_denied(client, db):
    """GitHub OAuth 経由で登録したユーザー (hashed_password=NULL) は ID入力ログイン不可 → 401。

    403 にするとユーザー名の存在・登録方法が確定してしまう（User Enumeration）ため、
    401 に統一してユーザー名・登録方法を漏洩しない（最小情報開示の原則）。
    """
    # コールバック経由ではなく DB 直接作成（hashed_password=None の GH OAuth ユーザーを模倣）
    from app.crud.user import create_user as db_create_user
    from app.schemas.user import UserCreate

    db_create_user(db, UserCreate(username=FAKE_GITHUB_USER["login"], password=None))

    # 同じ username で ID入力ログインを試みる → 401（ユーザー名漏洩させない）
    res = client.post(
        "/api/v1/auth/login",
        json={"username": FAKE_GITHUB_USER["login"], "password": "anypassword"},
    )
    assert res.status_code == 401


def test_login_cookie_enables_authenticated_request(client):
    """ログインで取得した Cookie で認証必須エンドポイントにアクセスできる。"""
    client.post(
        "/api/v1/auth/register",
        json={"username": "cookie_flow_user", "password": "pass9900"},
    )

    me_res = client.get("/api/v1/users/me")
    assert me_res.status_code == 200
    assert me_res.json()["username"] == "cookie_flow_user"
