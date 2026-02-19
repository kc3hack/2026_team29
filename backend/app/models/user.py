from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

if TYPE_CHECKING:
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True, nullable=False)
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    rank = Column(Integer, default=0)  # 0-9: 種子〜世界樹

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False)
    oauth_accounts = relationship("OAuthAccount", back_populates="user")
    badges = relationship("Badge", back_populates="user")
    quest_progress = relationship("QuestProgress", back_populates="user")
    skill_trees = relationship("SkillTree", back_populates="user")
