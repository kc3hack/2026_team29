"""QuestProgress スキーマ"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import QuestStatus


class QuestProgress(BaseModel):
    id: int
    quest_id: int
    status: QuestStatus
    started_at: datetime | None
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
