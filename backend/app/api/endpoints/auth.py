"""GitHub OAuth 認証エンドポイント (Issue #59, ADR 014)

フロー:
  GET /auth/github/login      → GitHub 認可ページへリダイレクト
  GET /auth/github/callback   → code 交換 → User 作成/取得
                                → JWT を httpOnly Cookie にセット → フロントへリダイレクト
  GET /auth/logout             → Cookie をクリアして返す

セッション管理方針 (ADR 014 更新):
  JWT (HS256, 有効期限 24h) を httpOnly; Secure; SameSite=Lax Cookie で発行する。
  httpOnly により JavaScript から Cookie へのアクセスを禁止し、XSS によるトークン盗取を防ぐ。
  フロントは Cookie を自動送信するため Authorization ヘッダー不要。
  ただし get_current_user は Authorization: Bearer <token> ヘッダーも受け付ける（テスト互換）。
"""

import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta, timezone

import httpx
import jwt
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud import oauth_account as crud_oauth
from app.crud import user as crud_user
from app.db.session import get_db
from app.schemas.oauth_account import OAuthAccountCreate, OAuthTokenUpdate
from app.schemas.user import UserCreate

router = APIRouter()

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"

# Cookie 名（フロントと共有する必要はない: httpOnly のため JS から読めない）
AUTH_COOKIE_NAME = "access_token"


# ---------------------------------------------------------------------------
# JWT ユーティリティ
# ---------------------------------------------------------------------------


def create_access_token(user_id: int) -> str:
    """user_id を含む JWT アクセストークンを発行する (ADR 014)。"""
    if not settings.JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY is not configured")
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "user_id": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def set_auth_cookie(response: Response, token: str) -> None:
    """JWT を httpOnly Cookie としてセットする。

    - httpOnly: JS からアクセス不可 → XSS によるトークン盗取を防止
    - Secure: HTTPS 経由のみ送信（開発環境では localhost のため False でも可）
    - SameSite=Lax: CSRF 対策（外部サイトからの POST リクエストでは送信しない）
    """
    is_https = not settings.FRONTEND_URL.startswith("http://localhost")
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=is_https,
        samesite="lax",
        max_age=settings.JWT_EXPIRE_HOURS * 3600,
        path="/",
    )


# ---------------------------------------------------------------------------
# CSRF 対策用 state (HMAC ベース、ステートレス: Redis 不要)
# ---------------------------------------------------------------------------


def _sign_state(raw_state: str) -> str:
    """state に HMAC 署名を付与する（10分ウィンドウ単位で有効）。"""
    window = int(time.time()) // 600
    sig = hmac.new(
        settings.JWT_SECRET_KEY.encode(),
        f"{raw_state}:{window}".encode(),
        hashlib.sha256,
    ).hexdigest()[:16]
    return f"{raw_state}.{sig}"


def _verify_state(signed_state: str) -> bool:
    """state の HMAC 署名を検証する（現在 ± 先の10分ウィンドウを許容）。"""
    if not settings.JWT_SECRET_KEY:
        return False
    try:
        raw_state, received_sig = signed_state.rsplit(".", 1)
    except ValueError:
        return False
    current_window = int(time.time()) // 600
    for window in (current_window, current_window - 1):
        expected_sig = hmac.new(
            settings.JWT_SECRET_KEY.encode(),
            f"{raw_state}:{window}".encode(),
            hashlib.sha256,
        ).hexdigest()[:16]
        if hmac.compare_digest(received_sig, expected_sig):
            return True
    return False


# ---------------------------------------------------------------------------
# エンドポイント
# ---------------------------------------------------------------------------


@router.get("/github/login", summary="GitHub OAuth ログイン開始")
def github_login() -> RedirectResponse:
    """GitHub の認可ページへリダイレクトする。

    CSRF 対策として HMAC 署名済み state パラメータを付与する。
    """
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=503, detail="GitHub OAuth は設定されていません (GITHUB_CLIENT_ID)"
        )
    state = _sign_state(secrets.token_urlsafe(24))
    # scope=read:user のみ要求（最小権限の原則）
    redirect_url = (
        f"{GITHUB_AUTHORIZE_URL}"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&scope=read:user"
        f"&state={state}"
    )
    return RedirectResponse(url=redirect_url)


@router.get("/github/callback", summary="GitHub OAuth コールバック")
def github_callback(
    code: str = Query(..., description="GitHub から返される認可コード"),
    state: str = Query(..., description="CSRF 対策 state パラメータ"),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    """GitHub OAuth コールバック処理。

    1. state 検証（CSRF 対策）
    2. code → GitHub アクセストークン交換
    3. GitHub ユーザー情報取得
    4. 既存ユーザー照合 or 新規 User + OAuthAccount 作成
    5. JWT を httpOnly Cookie にセットしてフロントエンドへリダイレクト

    JWT は URL パラメータに含めない（ブラウザ履歴・Referer ヘッダーへの漏洩防止）。
    """
    # --- 1. state 検証 ---
    if not _verify_state(state):
        raise HTTPException(status_code=400, detail="Invalid or expired state parameter")

    # --- 2. GitHub アクセストークン取得 ---
    try:
        with httpx.Client(timeout=10.0) as client:
            token_resp = client.post(
                GITHUB_TOKEN_URL,
                json={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                },
                headers={"Accept": "application/json"},
            )
        token_resp.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=502, detail=f"GitHub token exchange failed: {e}"
        ) from e

    token_data = token_resp.json()
    access_token: str | None = token_data.get("access_token")
    if not access_token:
        # GitHub は 200 でエラーを返すことがある
        error_desc = token_data.get("error_description", token_data.get("error", "No access token"))
        raise HTTPException(status_code=400, detail=error_desc)

    # --- 3. GitHub ユーザー情報取得 ---
    try:
        with httpx.Client(timeout=10.0) as client:
            user_resp = client.get(
                GITHUB_USER_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
        user_resp.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=502, detail=f"Failed to fetch GitHub user info: {e}"
        ) from e

    github_user = user_resp.json()
    github_user_id = str(github_user["id"])
    github_login_name: str = github_user["login"]

    # --- 4. 既存ユーザー照合 or 新規作成 ---
    existing_oauth = crud_oauth.get_by_provider_user_id(db, "github", github_user_id)

    if existing_oauth:
        # ログイン: アクセストークンを最新に更新（再暗号化保存）
        crud_oauth.update_oauth_tokens(
            db,
            existing_oauth.id,
            OAuthTokenUpdate(access_token=access_token),
        )
        db_user = crud_user.get_user(db, existing_oauth.user_id)
    else:
        # 新規登録: username の重複回避
        username = github_login_name
        if crud_user.get_user_by_username(db, username) is not None:
            username = f"{github_login_name}_{github_user_id}"

        # User 作成（SkillTree 6カテゴリの自動初期化も実行される）
        db_user = crud_user.create_user(db, UserCreate(username=username))

        # OAuthAccount 作成（GitHubトークンは暗号化保存: ADR 005）
        crud_oauth.create_oauth_account(
            db,
            OAuthAccountCreate(
                user_id=db_user.id,
                provider="github",
                provider_user_id=github_user_id,
                access_token=access_token,
            ),
        )

    if db_user is None:
        raise HTTPException(status_code=500, detail="User lookup failed after OAuth flow")

    # --- 5. JWT を httpOnly Cookie にセットしてフロントへリダイレクト ---
    # JWT を URL パラメータに含めない（ブラウザ履歴・Referer への漏洩防止）
    jwt_token = create_access_token(db_user.id)
    redirect = RedirectResponse(url=settings.FRONTEND_URL, status_code=302)
    set_auth_cookie(redirect, jwt_token)
    return redirect


@router.get("/logout", summary="ログアウト（Cookie クリア）")
def logout(response: Response) -> dict:
    """httpOnly Cookie を削除してログアウトする。

    フロント側のストレージ操作は不要。
    """
    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        path="/",
        httponly=True,
        samesite="lax",
    )
    return {"message": "ログアウトしました"}

