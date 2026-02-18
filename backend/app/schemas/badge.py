"""Badge スキーマ"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import BadgeCategory


class BadgeCreate(BaseModel):
    user_id: int
    category: BadgeCategory
    tier: int  # 1-3: Bronze/Silver/Gold


class Badge(BaseModel):
    id: int
    user_id: int
    category: BadgeCategory
    tier: int
    earned_at: datetime

    model_config = ConfigDict(from_attributes=True)
