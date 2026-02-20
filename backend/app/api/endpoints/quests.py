"""Quest / QuestProgress エンドポイント (Issue #53, #65, ADR 013)

Quest Read: 認証不要
QuestProgress (start/complete): 認証必須（user_id は JWT から取得: #65 対応）
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud import quest as crud_quest
from app.crud import quest_progress as crud_quest_progress
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.enums import QuestCategory
from app.models.user import User
from app.schemas.quest import Quest as QuestSchema
from app.schemas.quest_progress import QuestProgress as QuestProgressSchema

router = APIRouter()


# ---------------------------------------------------------------------------
# Quest（Read のみ: ADR 013）
# ---------------------------------------------------------------------------


@router.get("", response_model=list[QuestSchema])
def list_quests(
    category: QuestCategory | None = Query(None, description="カテゴリフィルタ"),
    db: Session = Depends(get_db),
) -> list[QuestSchema]:
    """クエスト一覧取得（カテゴリフィルタ対応）。"""
    if category is not None:
        return crud_quest.list_quests_by_category(db, category)
    from app.models.quest import Quest as QuestModel
    return db.query(QuestModel).all()


@router.get("/{quest_id}", response_model=QuestSchema)
def get_quest(quest_id: int, db: Session = Depends(get_db)) -> QuestSchema:
    """クエスト詳細取得。"""
    quest = crud_quest.get_quest(db, quest_id)
    if quest is None:
        raise HTTPException(status_code=404, detail="Quest not found")
    return quest


# ---------------------------------------------------------------------------
# QuestProgress（認証必須: user_id は JWT から取得 #65 対応, ADR 015）
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
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/{quest_id}/complete", response_model=QuestProgressSchema)
def complete_quest(
    quest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestProgressSchema:
    """クエスト完了。user_id は認証トークンから取得（ADR 015, Issue #65）。

    - 404: クエストが存在しない / 進捗が存在しない
    - 400: ステータスが IN_PROGRESS でない（未開始または既に完了済み）
    """
    if crud_quest.get_quest(db, quest_id) is None:
        raise HTTPException(status_code=404, detail="Quest not found")
    # IN_PROGRESS チェック（ADR 013 エラーハンドリング方針）
    progress = crud_quest_progress.get_quest_progress(db, current_user.id, quest_id)
    if progress is None:
        raise HTTPException(status_code=404, detail="Quest progress not found (not started)")
    from app.models.enums import QuestStatus
    if progress.status != QuestStatus.IN_PROGRESS.value:
        raise HTTPException(
            status_code=400,
            detail=f"Quest is not in progress (current status: {progress.status})",
        )
    try:
        return crud_quest_progress.complete_quest(db, current_user.id, quest_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
