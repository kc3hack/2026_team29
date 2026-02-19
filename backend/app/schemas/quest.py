"""Quest スキーマ"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

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


class Quest(BaseModel):
    id: int
    title: str
    description: str
    difficulty: int
    category: QuestCategory
    is_generated: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
