"""create profiles table

Revision ID: 0002_profiles
Revises: e3b4e47f8ec0
Create Date: 2026-02-18

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_profiles"
down_revision: Union[str, Sequence[str], None] = "e3b4e47f8ec0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("github_username", sa.String(), nullable=True),
        sa.Column("qiita_id", sa.String(), nullable=True),
        sa.Column("connpass_id", sa.String(), nullable=True),
        sa.Column("portfolio_url", sa.String(), nullable=True),
        sa.Column("portfolio_text", sa.Text(), nullable=True),
        sa.Column("last_analyzed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_profiles_id"), "profiles", ["id"], unique=False)
    op.create_index(op.f("ix_profiles_user_id"), "profiles", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_profiles_user_id"), table_name="profiles")
    op.drop_index(op.f("ix_profiles_id"), table_name="profiles")
    op.drop_table("profiles")
