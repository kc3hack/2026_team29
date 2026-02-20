"""SkillTree モデル - カテゴリ別スキルツリー（User 1:6）"""

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class SkillTree(Base):
    __tablename__ = "skill_trees"
    __table_args__ = (
        UniqueConstraint("user_id", "category", name="uq_skill_tree_user_category"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    category = Column(String, nullable=False)
    # SQLiteではBLOB型、PostgreSQLではJSONB型として保存（SQLAlchemyが自動変換）
    tree_data = Column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    generated_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="skill_trees")
