"""管理API（/admin）

アクセス制御: X-Admin-Key ヘッダーでAPIキー認証
Swagger UI: /admin/docs（認証必須）
"""

import secrets

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.rank import calculate_rank
from app.db.session import get_db
from app.models.user import User

# Admin専用のFastAPIアプリ（独立したSwagger UI用）
admin_app = FastAPI(
    title="Team29 Admin API",
    description="管理者専用API（認証必須）",
    version="0.1.0",
    docs_url=None,  # デフォルトの/docsを無効化
    redoc_url=None,  # ReDocを無効化
)


def verify_admin_key(x_admin_key: str | None = Header(None)) -> None:
    """管理APIキーを検証する

    リクエストヘッダー `X-Admin-Key` と環境変数 `ADMIN_API_KEY` を照合。
    未指定または不一致の場合は401 Unauthorizedを返す。
    """
    if not settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ADMIN_API_KEY is not configured on server",
        )
    if x_admin_key is None or not secrets.compare_digest(
        x_admin_key, settings.ADMIN_API_KEY
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin API key",
        )


@admin_app.get("/docs", include_in_schema=False)
async def admin_docs(request: Request, _: None = Depends(verify_admin_key)):
    """管理API専用のSwagger UI（認証必須）"""
    return get_swagger_ui_html(
        openapi_url="/admin/openapi.json",
        title="Team29 Admin API - Swagger UI",
    )


@admin_app.get("/openapi.json", include_in_schema=False)
async def admin_openapi(_: None = Depends(verify_admin_key)):
    """管理API専用のOpenAPIスキーマ（認証必須）"""
    return JSONResponse(admin_app.openapi())


@admin_app.post("/fix-user-ranks")
def fix_user_ranks(
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_key),
):
    """全ユーザーのランクを経験値から再計算して修正する

    認証: X-Admin-Key ヘッダーが必要
    """
    users = db.query(User).all()
    fixed_count = 0

    for user in users:
        expected_rank = calculate_rank(user.exp)
        if user.rank != expected_rank:
            user.rank = expected_rank
            fixed_count += 1

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {"fixed_count": fixed_count, "total_users": len(users)}
