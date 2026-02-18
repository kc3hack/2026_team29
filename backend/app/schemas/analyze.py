"""
ランク判定分析スキーマ
"""

from pydantic import BaseModel, Field


class RankAnalysisRequest(BaseModel):
    """ランク判定リクエスト"""

    github_username: str = Field(..., min_length=1, max_length=100, description="GitHub username")
    portfolio_text: str = Field(
        default="", max_length=5000, description="ポートフォリオ情報（任意）"
    )
    qiita_id: str = Field(default="", max_length=100, description="Qiita ID（任意）")
    other_info: str = Field(default="", max_length=2000, description="その他の活動情報（任意）")

    class Config:
        json_schema_extra = {
            "example": {
                "github_username": "octocat",
                "portfolio_text": "個人サイト: https://example.com",
                "qiita_id": "example_user",
                "other_info": "LeetCode参加者、エンジニアコミュニティ活動",
            }
        }


class RankAnalysisResponse(BaseModel):
    """ランク判定レスポンス"""

    percentile: float = Field(..., ge=0.0, le=100.0, description="パーセンタイル値（0-100）")
    rank: int = Field(..., ge=0, le=9, description="ランク（0-9）")
    rank_name: str = Field(..., description="ランク名（種子〜世界樹）")
    reasoning: str = Field(..., description="判定理由")

    class Config:
        json_schema_extra = {
            "example": {
                "percentile": 65.0,
                "rank": 4,
                "rank_name": "母樹",
                "reasoning": "複数の技術スタックでの実装経験と継続的なアウトプットが確認されました。",
            }
        }
