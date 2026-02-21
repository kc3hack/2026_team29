"""管理API（/admin）

アクセス制御: X-Admin-Key ヘッダーでAPIキー認証
Swagger UI: /admin/docs（認証必須）
"""

import secrets

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.rank import calculate_rank
from app.crud import quest as crud_quest
from app.db.session import get_db
from app.models.enums import QuestCategory
from app.models.user import User
from app.schemas.quest import Quest as QuestSchema
from app.schemas.quest import QuestCreate, QuestSummary
from app.services.quest_service import generate_handson_quest

# limit 値の上限（運用上大量取得を防ぐ）
_ADMIN_LIST_MAX = 200

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
# Quest 管理 (Issue #77: 管理者向け CRUD + LLM 生成)
# ---------------------------------------------------------------------------


@admin_app.get("/quests", response_model=list[QuestSummary])
def admin_list_quests(
    category: QuestCategory | None = None,
    difficulty: int | None = None,
    skip: int = Query(0, ge=0, description="スキップ件数（0以上）"),
    limit: int = Query(50, ge=1, le=_ADMIN_LIST_MAX, description=f"取得件数（1〜{_ADMIN_LIST_MAX}）"),
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_key),
) -> list[QuestSummary]:
    """クエスト一覧取得（description 除く、フィルタリング対応）。

    認証: X-Admin-Key ヘッダーが必要
    """
    return crud_quest.list_quests(db, skip=skip, limit=limit, category=category, difficulty=difficulty)


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


class AdminQuestGenerateRequest(BaseModel):
    """管理者向けクエスト生成リクエスト"""

    document_content: str = Field(..., min_length=10, max_length=10000, description="学習対象ドキュメント")
    user_rank: int = Field(..., ge=0, le=9, description="難易度（ランク 0-9: 種子〜世界樹）")
    user_skills: str = Field(default="", max_length=500, description="得意分野（オプション）")
    category: QuestCategory = Field(..., description="クエストカテゴリ")


def _steps_to_markdown(result: dict) -> str:
    """LLM 生成結果を Markdown 形式の description に変換する（ADR 012）。"""
    lines: list[str] = []

    objectives: list[str] = result.get("learning_objectives", [])
    if objectives:
        lines.append("## 学習目標\n")
        for obj in objectives:
            lines.append(f"- {obj}")
        lines.append("")

    for step in result.get("steps", []):
        step_num = step.get("step_number", 0)
        step_title = step.get("title", "Untitled")
        lines.append(f"## Step {step_num}: {step_title}\n")
        lines.append(step.get("description", ""))
        code: str = step.get("code_example", "")
        if code:
            lines.append(f"\n```\n{code}\n```")
        checkpoints: list[str] = step.get("checkpoints", [])
        if checkpoints:
            lines.append("\n**確認ポイント:**")
            for cp in checkpoints:
                lines.append(f"- {cp}")
        lines.append("")

    resources: list[str] = result.get("resources", [])
    if resources:
        lines.append("## 参考リソース\n")
        for r in resources:
            lines.append(f"- {r}")

    return "\n".join(lines)


@admin_app.post("/quests/generate", response_model=QuestSchema, status_code=201)
async def admin_generate_and_save_quest(
    request: AdminQuestGenerateRequest,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_key),
) -> QuestSchema:
    """LLM でクエストを生成し DB に保存する。

    認証: X-Admin-Key ヘッダーが必要

    - LLM が生成したタイトル・ステップを Markdown に変換して description に保存（ADR 012）
    - difficulty はリクエストの user_rank をそのまま使用（0-9）
    - is_generated=True で保存（通常クエストと区別可能）
    """
    try:
        result = await generate_handson_quest(
            document_content=request.document_content,
            user_rank=request.user_rank,
            user_skills=request.user_skills,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Quest generation failed: {str(e)}",
        )

    quest_in = QuestCreate(
        title=result["title"],
        description=_steps_to_markdown(result),
        difficulty=request.user_rank,
        category=request.category,
        is_generated=True,
    )
    try:
        return crud_quest.create_quest(db, quest_in)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save quest: {str(e)}",
        )
