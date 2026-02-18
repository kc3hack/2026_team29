"""
ランク判定APIエンドポイント

POST /api/v1/analyze/rank - ユーザーランクの判定
"""

from fastapi import APIRouter, HTTPException
from app.schemas.analyze import RankAnalysisRequest, RankAnalysisResponse
from app.services.rank_service import analyze_user_rank

router = APIRouter()


@router.post("/rank", response_model=RankAnalysisResponse)
async def analyze_rank(request: RankAnalysisRequest) -> RankAnalysisResponse:
    """
    ユーザーのランクをLLMで判定

    Args:
        request: ランク判定リクエスト

    Returns:
        RankAnalysisResponse: ランク判定結果

    Raises:
        HTTPException 500: LLM呼び出し失敗時

    Example:
        Request:
            {
                "github_username": "octocat",
                "portfolio_text": "個人サイト: https://example.com",
                "qiita_id": "example_user",
                "other_info": "LeetCode参加者"
            }

        Response:
            {
                "percentile": 65.0,
                "rank": 4,
                "rank_name": "母樹",
                "reasoning": "複数の技術スタックでの実装経験が確認されました。"
            }
    """
    try:
        result = await analyze_user_rank(
            github_username=request.github_username,
            portfolio_text=request.portfolio_text,
            qiita_id=request.qiita_id,
            other_info=request.other_info,
        )
        return RankAnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rank analysis failed: {str(e)}")
