"""create skill_trees table

Revision ID: 0007_skill_trees
Revises: 0006_quest_progress
Create Date: 2026-02-18

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007_skill_trees"
down_revision: Union[str, Sequence[str], None] = "0006_quest_progress"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "skill_trees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("tree_data", sa.JSON(), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "category", name="uq_skill_tree_user_category"),
    )
    op.create_index(op.f("ix_skill_trees_id"), "skill_trees", ["id"], unique=False)
    op.create_index(op.f("ix_skill_trees_user_id"), "skill_trees", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_skill_trees_user_id"), table_name="skill_trees")
    op.drop_index(op.f("ix_skill_trees_id"), table_name="skill_trees")
    op.drop_table("skill_trees")
