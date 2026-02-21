"""
ランク判定分析スキーマ

Issue #35: AI実装Phase 2 - モックAPIエンドポイント
- RankAnalysisRequest/Response: 既存（issue #36で実装済み）
- SkillTreeRequest/Response: スキルツリー生成（モック）
- QuestGenerationRequest/Response: 演習生成（モック）
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import QuestCategory, SkillCategory


class RankAnalysisRequest(BaseModel):
    """ランク判定リクエスト"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "github_username": "octocat",
                "portfolio_text": "個人サイト: https://example.com",
                "qiita_id": "example_user",
                "other_info": "LeetCode参加者、エンジニアコミュニティ活動",
            }
        }
    )

    github_username: str = Field(
        ..., min_length=1, max_length=100, description="GitHub username"
    )
    portfolio_text: str = Field(
        default="", max_length=5000, description="ポートフォリオ情報（任意）"
    )
    qiita_id: str = Field(default="", max_length=100, description="Qiita ID（任意）")
    other_info: str = Field(
        default="", max_length=2000, description="その他の活動情報（任意）"
    )


class RankAnalysisResponse(BaseModel):
    """ランク判定レスポンス"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "percentile": 80.0,
                "rank": 4,
                "rank_name": "母樹",
                "reasoning": "複数の技術スタックでの実装経験と継続的なアウトプットが確認されました。実務経験3年以上相当、上位20%に位置します。",
            }
        }
    )

    percentile: float = Field(
        ..., ge=0.0, le=100.0, description="上位パーセンタイル（100=最上位、0=最下位）"
    )
    rank: int = Field(..., ge=0, le=9, description="ランク（0=種子〜9=世界樹）")
    rank_name: str = Field(..., description="ランク名（種子〜世界樹）")
    reasoning: str = Field(..., description="判定理由")


# ====================================
# スキルツリー生成（Issue #35）
# ====================================


class SkillTreeRequest(BaseModel):
    """スキルツリー生成リクエスト（認証済みユーザー）"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category": "web",
            }
        }
    )

    category: SkillCategory = Field(..., description="スキルカテゴリ（6種類）")


class SkillTreeResponse(BaseModel):
    """スキルツリー生成レスポンス"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category": "web",
                "tree_data": {
                    "nodes": [
                        {
                            "id": "html-css",
                            "name": "HTML/CSS基礎",
                            "completed": True,
                            "description": "基本的なマークアップとスタイリング",
                            "prerequisites": [],
                            "estimated_hours": 20,
                        }
                    ],
                    "edges": [{"from": "html-css", "to": "js-basics"}],
                    "metadata": {
                        "total_nodes": 5,
                        "completed_nodes": 2,
                        "progress_percentage": 40.0,
                        "next_recommended": ["react", "typescript"],
                    },
                },
                "generated_at": "2026-02-20T12:00:00+09:00",
            }
        }
    )

    category: SkillCategory = Field(..., description="スキルカテゴリ")
    tree_data: dict[str, Any] = Field(
        ...,
        description="スキルツリーJSON構造（nodes, edges, metadata）",
    )
    generated_at: datetime = Field(..., description="生成日時")


# ====================================
# 演習生成（Issue #35）
# ====================================


class QuestResource(BaseModel):
    """演習リソース"""

    title: str = Field(..., description="リソースタイトル")
    url: str = Field(..., description="リソースURL")


class QuestGenerationRequest(BaseModel):
    """演習生成リクエスト"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": 1,
                "category": "web",
                "difficulty": 4,
                "document_text": "FastAPIのドキュメント...",
            }
        }
    )

    user_id: int = Field(..., gt=0, description="ユーザーID")
    category: QuestCategory = Field(..., description="クエストカテゴリ（6種類）")
    difficulty: int = Field(..., ge=0, le=9, description="難易度（0-9: ランクに対応）")
    document_text: str = Field(
        default="",
        max_length=100000,
        description="参考ドキュメント（RAG用、Phase 3で使用）",
    )


class QuestGenerationResponse(BaseModel):
    """演習生成レスポンス（モック実装用の拡張フィールド含む）"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 101,
                "title": "FastAPIで認証付きTodo API構築",
                "description": "JWT認証を実装したCRUD APIを作成",
                "difficulty": 4,
                "category": "web",
                "is_generated": True,
                "steps": [
                    "1. FastAPIプロジェクト初期化",
                    "2. SQLAlchemyでTodoモデル定義",
                ],
                "estimated_time_minutes": 120,
                "resources": [
                    {
                        "title": "FastAPI公式ドキュメント",
                        "url": "https://fastapi.tiangolo.com/ja/",
                    }
                ],
                "created_at": "2026-02-20T12:00:00+09:00",
            }
        }
    )

    id: int = Field(..., description="クエストID")
    title: str = Field(..., description="クエストタイトル")
    description: str = Field(..., description="クエスト説明")
    difficulty: int = Field(..., ge=0, le=9, description="難易度（0-9）")
    category: QuestCategory = Field(..., description="クエストカテゴリ")
    is_generated: bool = Field(..., description="AI生成フラグ")

    # モック実装専用フィールド（DB設計には含まれない）
    steps: list[str] = Field(..., description="実装手順リスト（モック実装でのみ使用）")
    estimated_time_minutes: int = Field(
        ..., gt=0, description="推定所要時間（分、モック実装でのみ使用）"
    )
    resources: list[QuestResource] = Field(
        ..., description="参考リソースリスト（モック実装でのみ使用）"
    )

    created_at: datetime = Field(..., description="作成日時")
