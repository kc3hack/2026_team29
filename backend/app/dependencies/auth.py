"""認証依存関数 (Issue #61, ADR 014)

FastAPI の Depends() で使う get_current_user を提供する。
JWT (Bearer Token) を Authorization ヘッダーから取得・検証し、
DB から User を返す。

Usage:
    from app.dependencies.auth import get_current_user

    @router.get("/users/me")
    def me(current_user: User = Depends(get_current_user)):
        ...
"""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud import user as crud_user
from app.db.session import get_db
from app.models.user import User

# Authorization: Bearer <token> ヘッダーを自動的に解析する
_bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """JWT を検証して認証済み User を返す依存関数。

    - 401: トークンなし / 署名不正 / 期限切れ
    - 404: トークンは正常だが DB に User が存在しない（削除済み等）

    Raises:
        HTTPException 401: 認証失敗
        HTTPException 404: ユーザー不在
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証トークンが無効または期限切れです",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: int | None = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンの有効期限が切れています",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exception

    db_user = crud_user.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )
    return db_user
