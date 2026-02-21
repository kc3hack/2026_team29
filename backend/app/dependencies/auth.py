"""認証依存関数 (Issue #61, ADR 014)

FastAPI の Depends() で使う get_current_user を提供する。

トークン取得優先順位:
  1. Cookie `access_token` (httpOnly) — ブラウザ経由の通常フロー (ADR 014)
  2. Authorization: Bearer <token> ヘッダー — テスト / API クライアント互換

Usage:
    from app.dependencies.auth import get_current_user

    @router.get("/users/me")
    def me(current_user: User = Depends(get_current_user)):
        ...
"""

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud import user as crud_user
from app.db.session import get_db
from app.models.user import User

# Authorization: Bearer <token> ヘッダー（auto_error=False: Cookie フォールバックのため）
_bearer_scheme = HTTPBearer(auto_error=False)


def _decode_token(token: str) -> int:
    """JWT を検証して user_id を返す。失敗時は HTTPException 401。"""
    # 二重防衛: 起動時検証（validate_jwt_config）を通過していても念のためここでも確認する。
    # 空キーで HS256 検証が通ってしまう脆弱性を防ぐ（ADR 014）。
    if not settings.JWT_SECRET_KEY or not settings.JWT_SECRET_KEY.strip():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWT_SECRET_KEY が設定されていません。サーバー管理者に連絡してください。",
        )
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証トークンが無効または期限切れです",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        try:
            return int(user_id_str)
        except (ValueError, TypeError):
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンの有効期限が切れています",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidSignatureError:
        # 署名検証失敗（改ざん検出）
        raise credentials_exception
    except jwt.DecodeError:
        # デコード失敗（不正なフォーマット）
        raise credentials_exception
    except jwt.PyJWTError:
        # その他のJWTエラー
        raise credentials_exception


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """JWT を検証して認証済み User を返す依存関数。

    Cookie（httpOnly）→ Authorization ヘッダーの順で検索する。
    どちらもない場合は 401 を返す。

    - 401: トークンなし / 署名不正 / 期限切れ / DB にユーザーが存在しない（削除済み等）
    """
    # 1. httpOnly Cookie から取得（ブラウザ通常フロー）
    token: str | None = request.cookies.get("access_token")

    # 2. Authorization: Bearer ヘッダーにフォールバック（テスト / API クライアント）
    if not token and credentials is not None:
        token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証が必要です",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = _decode_token(token)
    db_user = crud_user.get_user(db, user_id)
    if db_user is None:
        # 404 ではなく 401 を返す（ユーザーの存在有無を外部に漏らさない）
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証が必要です",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return db_user
