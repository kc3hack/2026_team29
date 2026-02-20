"""Badge スキーマ"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enums import BadgeCategory


class BadgeCreate(BaseModel):
    user_id: int
    category: BadgeCategory
    tier: int  # 1-3: Bronze/Silver/Gold

    @field_validator("tier")
    @classmethod
    def validate_tier(cls, v: int) -> int:
        if v < 1 or v > 3:
            raise ValueError("tier must be 1 (Bronze), 2 (Silver), or 3 (Gold)")
        return v


class Badge(BaseModel):
    id: int
    category: BadgeCategory
    tier: int
    earned_at: datetime

    model_config = ConfigDict(from_attributes=True)
