"""
ハンズオン演習生成APIエンドポイント

POST /api/v1/quest/generate - ドキュメントからハンズオン演習を生成
"""

from fastapi import APIRouter, HTTPException
from app.schemas.quest import QuestGenerationRequest, QuestGenerationResponse
from app.services.quest_service import generate_handson_quest

router = APIRouter()


@router.post("/generate", response_model=QuestGenerationResponse)
async def generate_quest(request: QuestGenerationRequest) -> QuestGenerationResponse:
    """
    ドキュメントからハンズオン演習を生成

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
