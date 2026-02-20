"""SkillTree スキーマ"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import SkillCategory


class SkillTree(BaseModel):
    id: int
    category: SkillCategory
    tree_data: dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
