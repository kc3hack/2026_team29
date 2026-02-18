"""create quest_progress table

Revision ID: 0006_quest_progress
Revises: 0005_quests
Create Date: 2026-02-18

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006_quest_progress"
down_revision: Union[str, Sequence[str], None] = "0005_quests"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quest_progress",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("quest_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["quest_id"], ["quests.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "quest_id", name="uq_progress_user_quest"),
    )
    op.create_index(op.f("ix_quest_progress_id"), "quest_progress", ["id"], unique=False)
    op.create_index(op.f("ix_quest_progress_quest_id"), "quest_progress", ["quest_id"], unique=False)
    op.create_index(op.f("ix_quest_progress_user_id"), "quest_progress", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_quest_progress_user_id"), table_name="quest_progress")
    op.drop_index(op.f("ix_quest_progress_quest_id"), table_name="quest_progress")
    op.drop_index(op.f("ix_quest_progress_id"), table_name="quest_progress")
    op.drop_table("quest_progress")
