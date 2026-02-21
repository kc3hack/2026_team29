"""add hashed_password to users

ID入力ログイン (Spec 2.1) のためにパスワードカラムを追加する。
- GitHub OAuth ユーザーは NULL のまま運用（nullable=True）。
- ID入力で登録したユーザーのみ PBKDF2-HMAC-SHA256 でハッシュ化したパスワードを格納する。

Revision ID: 0003_add_hashed_password
Revises: 0002_change_tree_data_to_jsonb
Create Date: 2026-02-21

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_add_hashed_password"
down_revision: Union[str, Sequence[str], None] = "0002_change_tree_data_to_jsonb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("hashed_password", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "hashed_password")
