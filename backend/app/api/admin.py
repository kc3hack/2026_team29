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
from app.crud import quest as crud_quest
from app.db.session import get_db
from app.models.user import User
from app.schemas.quest import Quest as QuestSchema
from app.schemas.quest import QuestCreate, QuestUpdate

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


# ---------------------------------------------------------------------------
# Quest 管理 (Issue #77: 管理者向け CRUD)
# 一覧・詳細取得は公開 GET /quests, GET /quests/{id} で対応するため管理 API には不要
# ---------------------------------------------------------------------------


@admin_app.post("/quests", response_model=QuestSchema, status_code=201)
def admin_create_quest(
    quest_in: QuestCreate,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_key),
) -> QuestSchema:
    """手動クエスト作成（ボディを直接埋める）。

    認証: X-Admin-Key ヘッダーが必要

    LLM を使わずに管理者が直接 title / description / difficulty / category を指定する。
    description は Markdown 形式で入力すること（ADR 012）。
    """
    return crud_quest.create_quest(db, quest_in)


@admin_app.put("/quests/{quest_id}", response_model=QuestSchema)
def admin_update_quest(
    quest_id: int,
    quest_in: QuestUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_key),
) -> QuestSchema:
    """クエスト部分更新（指定フィールドのみ上書き）。

    認証: X-Admin-Key ヘッダーが必要

    - 200: 更新成功
    - 404: 指定 ID のクエストが存在しない

    description を変更する場合は Markdown 形式で入力すること（ADR 012）。
    """
    updated = crud_quest.update_quest(db, quest_id, quest_in)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quest not found")
    return updated


@admin_app.delete("/quests/{quest_id}", status_code=204)
def admin_delete_quest(
    quest_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_key),
) -> None:
    """クエスト削除。

    認証: X-Admin-Key ヘッダーが必要

    - 204: 削除成功
    - 404: 指定 ID のクエストが存在しない
    """
    deleted = crud_quest.delete_quest(db, quest_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quest not found")
