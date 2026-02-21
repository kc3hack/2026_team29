"""Quest スキーマ"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import QuestCategory


class QuestCreate(BaseModel):
    title: str
    description: str
    difficulty: int  # 0-9: 対象ランク
    category: QuestCategory
    is_generated: bool = False

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: int) -> int:
        if v < 0 or v > 9:
            raise ValueError("difficulty must be 0-9 (rank: 種子〜世界樹)")
        return v


class QuestUpdate(BaseModel):
    """クエスト更新用スキーマ（全フィールド任意）。

    指定したフィールドのみ更新する。description は Markdown 形式（ADR 012）。
    フィールドを省略（未送信）= 更新しない。
    フィールドを明示的に null で送信した場合は 422 を返す（DB の nullable=False 列を保護）。
    """

    title: str | None = None
    description: str | None = None
    difficulty: int | None = None
    category: QuestCategory | None = None

    @model_validator(mode="after")
    def reject_explicit_null(self) -> "QuestUpdate":
        """明示的に null が送られたフィールドを 422 で弾く。"""
        non_nullable = ("title", "description", "difficulty", "category")
        for field in non_nullable:
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: int | None) -> int | None:
        if v is not None and (v < 0 or v > 9):
            raise ValueError("difficulty must be 0-9 (rank: 種子〜世界樹)")
        return v


class QuestSummary(BaseModel):
    """クエスト一覧用スキーマ（description 除外）。

    一覧表示時にMarkdown本文全体を転送しないための軽量スキーマ。
    演習内容は GET /api/v1/quest/{quest_id} の Quest スキーマで取得する（ADR 012）。
    """

    id: int
    title: str
    difficulty: int
    category: QuestCategory
    is_generated: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Quest(BaseModel):
    """クエスト詳細スキーマ（description 含む）。"""

    id: int
    title: str
    description: str
    difficulty: int
    category: QuestCategory
    is_generated: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# ハンズオン演習生成用スキーマ
# ============================================================


class QuestStep(BaseModel):
    """演習ステップ"""

    step_number: int = Field(..., ge=1, description="ステップ番号")
    title: str = Field(
        ..., min_length=1, max_length=200, description="ステップタイトル"
    )
    description: str = Field(..., description="手順の詳細説明")
    code_example: str = Field(default="", description="コード例")
    checkpoints: list[str] = Field(default_factory=list, description="確認ポイント")


class QuestGenerationRequest(BaseModel):
    """ハンズオン生成リクエスト"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document_content": "Reactの基本: コンポーネント、State、Props...",
                "user_rank": 2,
                "user_skills": "JavaScript, HTML/CSS",
            }
        }
    )

    document_content: str = Field(
        ..., min_length=10, max_length=10000, description="学習対象ドキュメント"
    )
    user_rank: int = Field(
        default=0, ge=0, le=9, description="ユーザーランク（省略時は0=初心者）"
    )
    user_skills: str = Field(
        default="", max_length=500, description="得意分野（オプション）"
    )


class QuestGenerationResponse(BaseModel):
    """ハンズオン生成レスポンス"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Reactでカウンターアプリを作ろう",
                "difficulty": "beginner",
                "estimated_time_minutes": 45,
                "learning_objectives": ["Stateの理解", "イベントハンドリング"],
                "steps": [
                    {
                        "step_number": 1,
                        "title": "プロジェクトのセットアップ",
                        "description": "create-react-appで新規プロジェクトを作成",
                        "code_example": "npx create-react-app counter-app",
                        "checkpoints": ["プロジェクトが起動した"],
                    }
                ],
                "resources": ["https://react.dev/"],
            }
        }
    )

    title: str = Field(..., description="演習タイトル")
    difficulty: str = Field(..., description="難易度（beginner/intermediate/advanced）")
    estimated_time_minutes: int = Field(..., ge=1, description="推定所要時間（分）")
    learning_objectives: list[str] = Field(..., description="学習目標")
    steps: list[QuestStep] = Field(..., min_length=1, description="演習ステップ")
    resources: list[str] = Field(default_factory=list, description="参考リソース")
