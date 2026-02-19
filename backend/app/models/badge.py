"""Badge モデル - バッジシステム（User 1:N）"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Badge(Base):
    __tablename__ = "badges"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "category", "tier", name="uq_badge_user_category_tier"
        ),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    category = Column(String, nullable=False)
    tier = Column(Integer, nullable=False)
    earned_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user = relationship("User", back_populates="badges")
