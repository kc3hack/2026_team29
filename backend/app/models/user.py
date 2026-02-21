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
    hashed_password = Column(String, nullable=True)  # ID入力ログイン用 (GitHub OAuthユーザーはNULL)
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

    # Relationships（cascade="all, delete-orphan" でユーザー削除時に関連レコードも削除）
    profile = relationship(
        "Profile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    oauth_accounts = relationship(
        "OAuthAccount", back_populates="user", cascade="all, delete-orphan"
    )
    badges = relationship("Badge", back_populates="user", cascade="all, delete-orphan")
    quest_progress = relationship(
        "QuestProgress", back_populates="user", cascade="all, delete-orphan"
    )
    skill_trees = relationship(
        "SkillTree", back_populates="user", cascade="all, delete-orphan"
    )
