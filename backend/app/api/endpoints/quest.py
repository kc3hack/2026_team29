"""Quest API エンドポイント（Issue #53, #57, #65）

エンドポイント仕様は ADR 013 参照。Markdown 保存方針は ADR 012 参照。

認証不要（コンテンツ提供）:
  GET    /api/v1/quest                      - クエスト一覧
  GET    /api/v1/quest/{quest_id}           - クエスト詳細
  POST   /api/v1/quest/generate             - ドキュメントからハンズオン演習を生成

認証必須（JWT Cookie / Bearer, ADR 015）:
  POST   /api/v1/quest/{quest_id}/start     - クエスト開始（user_id は JWT から取得）
  POST   /api/v1/quest/{quest_id}/complete  - クエスト完了（user_id は JWT から取得）
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import quest as crud_quest
from app.crud import quest_progress as crud_quest_progress
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.enums import QuestCategory, QuestStatus
from app.models.user import User
from app.schemas.quest import Quest as QuestSchema
from app.schemas.quest import QuestGenerationRequest, QuestGenerationResponse, QuestSummary
from app.schemas.quest_progress import QuestProgress as QuestProgressSchema
from app.services.quest_service import generate_handson_quest
from app.services.badge_service import award_builder_badge_if_eligible

router = APIRouter()


# ---------------------------------------------------------------------------
# Quest CRUD
# ---------------------------------------------------------------------------


@router.get("", response_model=list[QuestSummary])
def list_quests(
    category: QuestCategory | None = None,
    difficulty: int | None = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[QuestSummary]:
    """クエスト一覧取得。description は除外（ADR 012: 軽量化のため）。
    演習詳細は GET /api/v1/quest/{quest_id} で取得すること。
    category・difficulty でフィルタリング可能。
    """
    return crud_quest.list_quests(
        db, skip=skip, limit=limit, category=category, difficulty=difficulty
    )


@router.get("/{quest_id}", response_model=QuestSchema)
def get_quest(quest_id: int, db: Session = Depends(get_db)) -> QuestSchema:
    """クエスト詳細取得。"""
    quest = crud_quest.get_quest(db, quest_id)
    if quest is None:
        raise HTTPException(status_code=404, detail="Quest not found")
    return quest


# ---------------------------------------------------------------------------
# QuestProgress（認証必須: user_id は JWT から取得, ADR 015, #65）
# ---------------------------------------------------------------------------


@router.post("/{quest_id}/start", response_model=QuestProgressSchema, status_code=201)
def start_quest(
    quest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestProgressSchema:
    """クエスト開始。user_id は認証トークンから取得（ADR 015, Issue #65）。

    - 404: クエストが存在しない
    - 409: 既に開始済み（UniqueConstraint 違反）
    """
    if crud_quest.get_quest(db, quest_id) is None:
        raise HTTPException(status_code=404, detail="Quest not found")
    try:
        return crud_quest_progress.start_quest(db, current_user.id, quest_id)
    except ValueError:
        # 内部実装（user_id/quest_id 等）をクライアントに露出しないよう固定文言にマッピング
        progress = crud_quest_progress.get_quest_progress(db, current_user.id, quest_id)
        if progress is not None:
            if progress.status == QuestStatus.IN_PROGRESS.value:
                raise HTTPException(status_code=409, detail="Quest already started")
            if progress.status == QuestStatus.COMPLETED.value:
                raise HTTPException(status_code=409, detail="Quest already completed")
        raise HTTPException(status_code=409, detail="Could not start quest")


@router.post("/{quest_id}/complete", response_model=QuestProgressSchema)
def complete_quest(
    quest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestProgressSchema:
    """クエスト完了。user_id は認証トークンから取得（ADR 015, Issue #65）。
    
    クエスト完了時にBUILDERバッジを自動付与（Issue #121）。

    - 404: クエストが存在しない / 進捗が存在しない
    - 400: ステータスが IN_PROGRESS でない（未開始または既に完了済み）
    """
    if crud_quest.get_quest(db, quest_id) is None:
        raise HTTPException(status_code=404, detail="Quest not found")
    progress = crud_quest_progress.get_quest_progress(db, current_user.id, quest_id)
    if progress is None:
        raise HTTPException(status_code=404, detail="Quest progress not found (not started)")
    if progress.status != QuestStatus.IN_PROGRESS.value:
        raise HTTPException(
            status_code=400,
            detail=f"Quest is not in progress (current status: {progress.status})",
        )
    try:
        result = crud_quest_progress.complete_quest(db, current_user.id, quest_id)
        
        # クエスト完了後、BUILDERバッジを付与（Issue #121）
        award_builder_badge_if_eligible(db, current_user.id)
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# LLM生成
# ---------------------------------------------------------------------------


@router.post("/generate", response_model=QuestGenerationResponse)
async def generate_quest(request: QuestGenerationRequest) -> QuestGenerationResponse:
    """
    ドキュメントからハンズオン演習を生成（Issue #57）

    Args:
        request: ハンズオン生成リクエスト

    Returns:
        QuestGenerationResponse: 生成された演習

    Raises:
        HTTPException 500: LLM呼び出し失敗時

    Example:
        Request:
            {
                "document_content": "Reactの基本: コンポーネント、State、Props...",
                "user_rank": 2,
                "user_skills": "JavaScript, HTML/CSS"
            }

        Response:
            {
                "title": "Reactでカウンターアプリを作ろう",
                "difficulty": "beginner",
                "estimated_time_minutes": 45,
                "learning_objectives": ["Stateの理解", "イベントハンドリング"],
                "steps": [...],
                "resources": ["https://react.dev/"]
            }
    """
    try:
        result = await generate_handson_quest(
            document_content=request.document_content,
            user_rank=request.user_rank,
            user_skills=request.user_skills,
        )
        return QuestGenerationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quest generation failed: {str(e)}")
