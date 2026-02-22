"""GitHub OAuth 認証エンドポイント (Issue #59, ADR 014)

フロー:
  GET /auth/github/login      → GitHub 認可ページへリダイレクト
  GET /auth/github/callback   → code 交換 → User 作成/取得
                                → JWT を httpOnly Cookie にセット → フロントへリダイレクト
  POST /auth/logout            → Cookie をクリアして返す

セッション管理方針 (ADR 014 更新):
  JWT (HS256, 有効期限 24h) を httpOnly; Secure; SameSite=Lax Cookie で発行する。
  httpOnly により JavaScript から Cookie へのアクセスを禁止し、XSS によるトークン盗取を防ぐ。
  フロントは Cookie を自動送信するため Authorization ヘッダー不要。
  ただし get_current_user は Authorization: Bearer <token> ヘッダーも受け付ける（テスト互換）。
"""

import hashlib
import hmac
import logging
import secrets
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import httpx
import jwt
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.password import verify_password
from app.crud import oauth_account as crud_oauth
from app.crud import user as crud_user
from app.crud import profile as crud_profile
from app.db.session import get_db
from app.schemas.oauth_account import OAuthAccountCreate, OAuthTokenUpdate
from app.schemas.user import UserCreate
from app.schemas.profile import ProfileCreate

logger = logging.getLogger(__name__)
router = APIRouter()

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"

# Cookie 名（フロントと共有する必要はない: httpOnly のため JS から読めない）
AUTH_COOKIE_NAME = "access_token"

# state HMAC のドメイン分離ラベル（JWT署名と同じ鍵を流用するため用途を明示して鍵空間を分離）
_STATE_HMAC_CTX = b"oauth:state:v1:"


# ---------------------------------------------------------------------------
# JWT ユーティリティ
# ---------------------------------------------------------------------------


def create_access_token(user_id: int) -> str:
    """user_id を含む JWT アクセストークンを発行する (ADR 014)。"""
    if not settings.JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY is not configured")
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),  # RFC 7519 標準クレーム（文字列型）
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def set_auth_cookie(response: Response, token: str) -> None:
    """JWT を httpOnly Cookie としてセットする。

    - httpOnly: JS からアクセス不可 → XSS によるトークン盗取を防止
    - Secure: HTTPS 経由のみ送信（開発環境では localhost のため False でも可）
    - SameSite=None: 異なるドメイン間（Vercel ↔ Render）でCookie送信
    """
    is_https = urlparse(settings.FRONTEND_URL).scheme == "https"
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=is_https,
        samesite="none" if is_https else "lax",
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
        _STATE_HMAC_CTX + f"{raw_state}:{window}".encode(),
        hashlib.sha256,
    ).hexdigest()[:32]
    return f"{raw_state}.{sig}"


def _verify_state(signed_state: str) -> bool:
    """state の HMAC 署名を検証する（現在および直前の10分ウィンドウを許容）。"""
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
            _STATE_HMAC_CTX + f"{raw_state}:{window}".encode(),
            hashlib.sha256,
        ).hexdigest()[:32]
        if hmac.compare_digest(received_sig, expected_sig):
            return True
    return False


# ---------------------------------------------------------------------------
# エンドポイント
# ---------------------------------------------------------------------------


@router.get("/github/login", summary="GitHub OAuth ログイン開始")
def github_login() -> RedirectResponse:
    """GitHub の認可ページへリダイレクトする。

    CSRF 対策として HMAC 署名済み state パラメータを付与し、
    同じ値を httpOnly Cookie (oauth_state) にセットしてセッションへバインドする。
    コールバック時に Cookie と query param が一致することを検証することで
    Login CSRF（RFC 6749 Section 10.12）を防ぐ。
    """
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=503,
            detail="GitHub OAuth は設定されていません (GITHUB_CLIENT_ID)",
        )
    # JWT 署名用設定が未整備の場合は HMAC を安全に生成できないため早期に失敗させる
    if (
        not getattr(settings, "JWT_SECRET_KEY", None)
        or not settings.JWT_SECRET_KEY.strip()
    ):
        raise HTTPException(
            status_code=503, detail="JWT 設定が正しくありません (JWT_SECRET_KEY)"
        )
    if not getattr(settings, "JWT_ALGORITHM", None):
        raise HTTPException(
            status_code=503, detail="JWT 設定が正しくありません (JWT_ALGORITHM)"
        )
    state = _sign_state(secrets.token_urlsafe(24))
    # scope: read:user (ユーザー情報) + repo (プライベートリポジトリ含む全リポジトリ情報)
    # ランク判定にGitHub統計情報が必要なため、repoスコープを要求
    redirect_url = (
        f"{GITHUB_AUTHORIZE_URL}"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&scope=read:user repo"
        f"&state={state}"
    )
    resp = RedirectResponse(url=redirect_url)
    is_https = urlparse(settings.FRONTEND_URL).scheme == "https"
    # RFC 6749 s.10.12: state をブラウザセッションにバインドする（Login CSRF 対策）
    resp.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=is_https,
        samesite="none" if is_https else "lax",
        max_age=600,  # 10分（HMAC ウィンドウと同期）
        path="/",
    )
    return resp


@router.get("/github/callback", summary="GitHub OAuth コールバック")
async def github_callback(
    request: Request,
    code: str = Query(..., description="GitHub から返される認可コード"),
    state: str = Query(..., description="CSRF 対策 state パラメータ"),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    """GitHub OAuth コールバック処理。

    1. state 検証（CSRF 対策: Cookie バインディング + HMAC 検証）
    2. code → GitHub アクセストークン交換
    3. GitHub ユーザー情報取得
    4. 既存ユーザー照合 or 新規 User + OAuthAccount 作成
    5. JWT を httpOnly Cookie にセットしてフロントエンドへリダイレクト

    JWT は URL パラメータに含めない（ブラウザ履歴・Referer ヘッダーへの漏洩防止）。
    """
    # --- 1. state 検証（Login CSRF 対策: RFC 6749 s.10.12）---
    # Cookie に保存した state と query param の state が一致するか検証する。
    # これにより「攻撃者が取得した state を被害者に踏ませる」Login CSRF を防ぐ。
    state_cookie = request.cookies.get("oauth_state")
    if not state_cookie or not secrets.compare_digest(state_cookie, state):
        raise HTTPException(
            status_code=400, detail="Invalid or expired state parameter"
        )
    # さらに HMAC 署名を検証してサーバー発行の state かを確認する
    if not _verify_state(state):
        raise HTTPException(
            status_code=400, detail="Invalid or expired state parameter"
        )

    # --- 2. GitHub アクセストークン取得 ---
    # 環境変数未設定時は外部 API を呼ばずに早期に 503 を返す（運用上の切り分け用）
    github_client_id = settings.GITHUB_CLIENT_ID
    github_client_secret = settings.GITHUB_CLIENT_SECRET
    if (
        not github_client_id
        or not str(github_client_id).strip()
        or not github_client_secret
        or not str(github_client_secret).strip()
    ):
        raise HTTPException(
            status_code=503,
            detail="GitHub OAuth は設定されていません (GITHUB_CLIENT_ID / GITHUB_CLIENT_SECRET)",
        )
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            token_resp = await client.post(
                GITHUB_TOKEN_URL,
                json={
                    "client_id": github_client_id,
                    "client_secret": github_client_secret,
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
        error_desc = token_data.get(
            "error_description", token_data.get("error", "No access token")
        )
        raise HTTPException(status_code=400, detail=error_desc)

    # --- 3. GitHub ユーザー情報取得 ---
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            user_resp = await client.get(
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
    github_user_id_raw = github_user.get("id")
    github_login_name: str | None = github_user.get("login")
    if not github_user_id_raw or not github_login_name:
        raise HTTPException(
            status_code=502, detail="GitHub ユーザー情報の取得に失敗しました"
        )
    github_user_id = str(github_user_id_raw)

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

        # 既存ユーザーでもProfileが存在しない場合は作成（マイグレーション対策: Issue #71）
        if db_user and not crud_profile.get_profile_by_user_id(db, db_user.id):
            try:
                crud_profile.create_profile(
                    db,
                    ProfileCreate(
                        user_id=db_user.id,
                        github_username=github_login_name,
                    ),
                )
            except Exception as e:
                # Profileの作成に失敗してもログインは継続（Warning のみ）
                logger.warning(
                    f"Failed to create profile for user_id={db_user.id}: {e}"
                )
    else:
        # 新規登録: username の重複回避
        username = github_login_name
        if crud_user.get_user_by_username(db, username) is not None:
            username = f"{github_login_name}_{github_user_id}"

        # User と OAuthAccount と Profile を同一トランザクションで作成（アトミック性保証）
        # commit=False にして全てを flush した後、一括 commit する。
        # これにより「User だけが永続化されるゾンビレコード」を防ぐ。
        try:
            db_user = crud_user.create_user(
                db, UserCreate(username=username), commit=False
            )
            # OAuthAccount 作成（GitHubトークンは暗号化保存: ADR 005）
            crud_oauth.create_oauth_account(
                db,
                OAuthAccountCreate(
                    user_id=db_user.id,
                    provider="github",
                    provider_user_id=github_user_id,
                    access_token=access_token,
                ),
                commit=False,
            )
            # Profile 作成（スキルツリー生成に必要: Issue #71）
            crud_profile.create_profile(
                db,
                ProfileCreate(
                    user_id=db_user.id,
                    github_username=github_login_name,
                ),
                commit=False,
            )
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(
                f"User registration failed: {type(e).__name__}: {e}", exc_info=True
            )
            raise HTTPException(
                status_code=500, detail=f"ユーザー登録に失敗しました: {str(e)}"
            ) from e
        db.refresh(db_user)  # commit 後に refresh（rollback 対象外）

    if db_user is None:
        raise HTTPException(
            status_code=500, detail="User lookup failed after OAuth flow"
        )

    logger.info(f"[DEBUG] About to start rank analysis for user {db_user.id}")

    # --- 4.5. GitHub統計情報を取得してランク判定を実行 (Issue #105) ---
    # OAuth完了時に自動でランク判定を実行し、ユーザーのrankとexpを更新する。
    # GitHub API障害時でもログインは継続する（Warning のみ）。
    try:
        from app.services.github_stats_service import fetch_github_user_stats
        from app.services.rank_service import analyze_user_rank_from_github

        logger.info(f"Starting auto rank analysis for user {db_user.id}")

        # GitHub統計情報を取得
        github_stats = await fetch_github_user_stats(access_token)

        # ユーザーのProfileを取得（補足情報として使用）
        user_profile = crud_profile.get_profile_by_user_id(db, db_user.id)

        # LLMでランク判定を実行
        rank_result = await analyze_user_rank_from_github(
            github_stats=github_stats, profile=user_profile
        )

        # ユーザーのランクと経験値を更新
        db_user.rank = rank_result["rank"]
        db_user.exp = rank_result.get("estimated_exp", 0)
        db.commit()
        db.refresh(db_user)

        logger.info(
            f"Auto rank analysis completed for user {db_user.id}: "
            f"rank={rank_result['rank']}, exp={rank_result.get('estimated_exp', 0)}"
        )
    except Exception as e:
        # ランク判定失敗してもOAuthログインは継続（デフォルト値で運用）
        logger.warning(
            f"Auto rank analysis failed for user {db_user.id}: {e}",
            exc_info=True,  # スタックトレースを出力
        )
        # デフォルト値はモデルの初期値（rank=0: 種子）を使用

    logger.info(f"[DEBUG] Rank analysis section completed for user {db_user.id}")

    # --- 4.6. GitHub連携バッジを付与 (Issue #121) ---
    # GitHub OAuth認証成功時、初回のみGitHub連携バッジを付与する
    try:
        from app.services.badge_service import award_github_badge
        
        github_badge = award_github_badge(db, db_user.id)
        if github_badge:
            logger.info(f"Awarded GitHub badge to user {db_user.id}")
    except Exception as e:
        # バッジ付与失敗してもOAuthログインは継続
        logger.warning(
            f"GitHub badge award failed for user {db_user.id}: {e}",
            exc_info=True,
        )

    # --- 5. JWT を httpOnly Cookie にセットしてフロントへリダイレクト ---
    # JWT を URL パラメータに含めない（ブラウザ履歴・Referer への漏洩防止）
    jwt_token = create_access_token(db_user.id)
    # GitHub OAuth 成功後はダッシュボードへリダイレクト（Issue #74）
    dashboard_url = f"{settings.FRONTEND_URL}/dashboard"
    redirect = RedirectResponse(url=dashboard_url, status_code=302)
    set_auth_cookie(redirect, jwt_token)
    # oauth_state Cookie を使用済みにする（ワンタイム化）
    is_https = urlparse(settings.FRONTEND_URL).scheme == "https"
    redirect.delete_cookie(
        key="oauth_state",
        path="/",
        httponly=True,
        secure=is_https,
        samesite="none" if is_https else "lax",
    )
    return redirect


@router.post("/logout", summary="ログアウト（Cookie クリア）")
def logout(response: Response) -> dict:
    """httpOnly Cookie を削除してログアウトする。

    フロント側のストレージ操作は不要。
    Cookie 削除時は発行時と同じ属性 (secure / samesite / path) を揃える必要がある。
    本番 (HTTPS) で secure=True を付け忘れるとブラウザが Cookie を削除しない。
    """
    is_https = urlparse(settings.FRONTEND_URL).scheme == "https"
    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=is_https,
        samesite="none" if is_https else "lax",
    )
    return {"message": "ログアウトしました"}


# ---------------------------------------------------------------------------
# ID 入力認証 (Spec 2.1: "GitHub OAuth または ID入力でログイン")
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    """username + password リクエストボディ。

    バリデーション:
    - username: 1〜72文字（空文字不可・ADR 017）
    - password: 1〜128文字（空文字不可・PBKDF2 DoS 対策・ADR 017）
    いずれも超過・未満の場合は自動的に 422 Unprocessable Entity を返す。
    """

    username: str = Field(min_length=1, max_length=72)
    password: str = Field(min_length=1, max_length=128)


@router.post("/register", summary="username + password 新規登録", status_code=201)
def register_by_username(
    body: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> dict:
    """username + password で新規アカウントを作成し JWT Cookie を返す（Spec 2.1: ID入力フロー）。

    - username が既に存在する場合は 409 Conflict。
    - 競合状態（TOCTOU）対策: IntegrityError（UNIQUE 制約違反）を 409 として返す。
    """
    try:
        db_user = crud_user.create_user(
            db, UserCreate(username=body.username, password=body.password)
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="username が既に使用されています")

    try:
        token = create_access_token(db_user.id)
    except ValueError:
        # 二重防衛: validate_jwt_config() を通過していれば通常ここには来ない
        raise HTTPException(
            status_code=503,
            detail="JWT_SECRET_KEY が設定されていません。サーバー管理者に連絡してください。",
        )
    set_auth_cookie(response, token)
    return {"message": "登録しました", "user_id": db_user.id}


@router.post("/login", summary="username + password ログイン")
def login_by_username(
    body: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> dict:
    """username + password で既存アカウントを認証し JWT Cookie を返す。

    - username が存在しない場合は 401（ユーザー列挙防止のため「存在しない」とは返さない）。
    - GitHub OAuth 経由で登録したユーザー（hashed_password=NULL）も 401（登録方法を含めたユーザー列挙防止のため）。
    """
    _INVALID = HTTPException(
        status_code=401,
        detail="ユーザー名またはパスワードが正しくありません",
        headers={"WWW-Authenticate": "Bearer"},
    )

    db_user = crud_user.get_user_by_username(db, body.username)

    if db_user is None:
        raise _INVALID
    elif db_user.hashed_password is None:
        # GitHub OAuth 経由で登録したユーザー: ID入力ログイン不可
        # 403 にするとユーザー名の存在が確定してしまう（User Enumeration）ため
        # 401 に統一してユーザー名・登録方法を漏洩しない（最小情報開示の原則）
        raise _INVALID
    else:
        # 既存ユーザー: PBKDF2-SHA256 検証
        if not verify_password(body.password, db_user.hashed_password):
            raise _INVALID

    try:
        token = create_access_token(db_user.id)
    except ValueError:
        # 二重防衛: validate_jwt_config() を通過していれば通常ここには来ない
        raise HTTPException(
            status_code=503,
            detail="JWT_SECRET_KEY が設定されていません。サーバー管理者に連絡してください。",
        )
    set_auth_cookie(response, token)
    return {"message": "ログインしました", "user_id": db_user.id}
