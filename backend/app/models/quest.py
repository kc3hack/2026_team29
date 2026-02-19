"""Quest モデル - 演習/クエスト（独立テーブル）"""

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Quest(Base):
    __tablename__ = "quests"

    id = Column(Integer, primary_key=True)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(Integer, nullable=False)  # 0-9: 対象ランク（種子〜世界樹）
    category = Column(String, nullable=False)
    is_generated = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    quest_progress = relationship("QuestProgress", back_populates="quest")
