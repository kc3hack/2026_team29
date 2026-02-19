"""create badges table

Revision ID: 0004_badges
Revises: 0003_oauth_accounts
Create Date: 2026-02-18

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_badges"
down_revision: Union[str, Sequence[str], None] = "0003_oauth_accounts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "badges",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("tier", sa.Integer(), nullable=False),
        sa.Column("earned_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "category", "tier", name="uq_badge_user_category_tier"),
    )
    op.create_index(op.f("ix_badges_user_id"), "badges", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_badges_user_id"), table_name="badges")
    op.drop_table("badges")
