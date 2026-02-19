"""Profile モデル - 外部連携情報（User 1:1）"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True
    )

    github_username = Column(String, nullable=True)
    qiita_id = Column(String, nullable=True)
    connpass_id = Column(String, nullable=True)
    portfolio_url = Column(String, nullable=True)
    portfolio_text = Column(Text, nullable=True)
    last_analyzed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="profile")
