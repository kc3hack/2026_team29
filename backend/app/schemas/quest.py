"""Quest スキーマ"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import QuestCategory


class QuestCreate(BaseModel):
    title: str
    description: str
    difficulty: int  # 0-9: 対象ランク
    category: QuestCategory
    is_generated: bool = False


class Quest(BaseModel):
    id: int
    title: str
    description: str
    difficulty: int
    category: QuestCategory
    is_generated: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
