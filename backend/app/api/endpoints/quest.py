"""Quest API エンドポイント（Issue #53, #57）

エンドポイント仕様は ADR 013 参照。
Markdown 保存方針は ADR 012 参照。

GET    /api/v1/quest                      - クエスト一覧
GET    /api/v1/quest/{quest_id}           - クエスト詳細
POST   /api/v1/quest/{quest_id}/start     - クエスト開始
POST   /api/v1/quest/{quest_id}/complete  - クエスト完了
POST   /api/v1/quest/generate             - LLMによる演習生成
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import quest as crud_quest
from app.crud import quest_progress as crud_quest_progress
from app.crud import user as crud_user
from app.db.session import get_db
from app.models.enums import QuestCategory, QuestStatus
from app.schemas.quest import Quest as QuestSchema
from app.schemas.quest import QuestGenerationRequest, QuestGenerationResponse
from app.schemas.quest_progress import QuestProgress as QuestProgressSchema
from app.schemas.quest_progress import QuestProgressComplete, QuestProgressStart
from app.services.quest_service import generate_handson_quest

router = APIRouter()


# ---------------------------------------------------------------------------
# Quest CRUD
# ---------------------------------------------------------------------------


@router.get("", response_model=list[QuestSchema])
def list_quests(
    category: QuestCategory | None = None,
    difficulty: int | None = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[QuestSchema]:
    """クエスト一覧取得。category・difficulty でフィルタリング可能。"""
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
# QuestProgress
# ---------------------------------------------------------------------------


@router.post("/{quest_id}/start", response_model=QuestProgressSchema, status_code=201)
def start_quest(
    quest_id: int,
    progress_in: QuestProgressStart,
    db: Session = Depends(get_db),
) -> QuestProgressSchema:
    """クエスト開始。既に開始済み/完了済みの場合は 409。"""
    if crud_quest.get_quest(db, quest_id) is None:
        raise HTTPException(status_code=404, detail="Quest not found")
    if crud_user.get_user(db, progress_in.user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        return crud_quest_progress.start_quest(
            db, user_id=progress_in.user_id, quest_id=quest_id
        )
    except ValueError:
        progress = crud_quest_progress.get_quest_progress(
            db, user_id=progress_in.user_id, quest_id=quest_id
        )
        if progress is not None and progress.status == QuestStatus.COMPLETED:
            detail = "Quest already completed"
        else:
            detail = "Quest already started"
        raise HTTPException(status_code=409, detail=detail)


@router.post("/{quest_id}/complete", response_model=QuestProgressSchema)
def complete_quest(
    quest_id: int,
    progress_in: QuestProgressComplete,
    db: Session = Depends(get_db),
) -> QuestProgressSchema:
    """クエスト完了。IN_PROGRESS でない場合は 400。"""
    if crud_quest.get_quest(db, quest_id) is None:
        raise HTTPException(status_code=404, detail="Quest not found")
    progress = crud_quest_progress.get_quest_progress(
        db, user_id=progress_in.user_id, quest_id=quest_id
    )
    if progress is None or progress.status != QuestStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Quest not in progress")
    return crud_quest_progress.complete_quest(
        db, user_id=progress_in.user_id, quest_id=quest_id
    )


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
