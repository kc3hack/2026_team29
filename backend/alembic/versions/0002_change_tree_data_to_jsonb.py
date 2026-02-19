"""change_tree_data_to_jsonb (issue #45)

Revision ID: 0002_change_tree_data_to_jsonb
Revises: 0001_all_tables
Create Date: 2026-02-19 14:07:37.523910

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = "0002_change_tree_data_to_jsonb"
down_revision: Union[str, Sequence[str], None] = "0001_all_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """SkillTree.tree_dataをJSON型からJSONB型(BLOB)に変更"""
    bind = op.get_bind()

    if bind.dialect.name == "postgresql":
        # PostgreSQL: JSON型 → JSONB型に変更
        op.alter_column(
            "skill_trees",
            "tree_data",
            type_=JSONB,
            existing_type=sa.JSON(),
            existing_nullable=False,
            postgresql_using="tree_data::jsonb",
        )
    elif bind.dialect.name == "sqlite":
        # SQLite: JSON型(TEXT) → BLOB型に変更
        # SQLiteではALTER COLUMNによる型変更が非対応のため、テーブル再作成が必要
        op.execute("""
            CREATE TABLE skill_trees_new (
                id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                category VARCHAR NOT NULL,
                tree_data BLOB NOT NULL,
                generated_at DATETIME,
                PRIMARY KEY (id),
                FOREIGN KEY(user_id) REFERENCES users (id),
                CONSTRAINT uq_skill_tree_user_category UNIQUE (user_id, category)
            )
        """)

        # データ移行（JSON文字列をBLOBに変換）
        op.execute("""
            INSERT INTO skill_trees_new (id, user_id, category, tree_data, generated_at)
            SELECT id, user_id, category, tree_data, generated_at
            FROM skill_trees
        """)

        # インデックスを削除
        op.execute("DROP INDEX IF EXISTS ix_skill_trees_user_id")

        # 旧テーブルを削除
        op.execute("DROP TABLE skill_trees")

        # 新テーブルをリネーム
        op.execute("ALTER TABLE skill_trees_new RENAME TO skill_trees")

        # インデックスを再作成
        op.create_index(
            "ix_skill_trees_user_id", "skill_trees", ["user_id"], unique=False
        )


def downgrade() -> None:
    """JSONB型(BLOB)からJSON型に戻す"""
    bind = op.get_bind()

    if bind.dialect.name == "postgresql":
        # PostgreSQL: JSONB型 → JSON型に戻す
        op.alter_column(
            "skill_trees",
            "tree_data",
            type_=sa.JSON(),
            existing_type=JSONB,
            existing_nullable=False,
            postgresql_using="tree_data::json",
        )
    elif bind.dialect.name == "sqlite":
        # SQLite: BLOB型 → JSON型(TEXT)に戻す
        op.execute("""
            CREATE TABLE skill_trees_old (
                id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                category VARCHAR NOT NULL,
                tree_data JSON NOT NULL,
                generated_at DATETIME,
                PRIMARY KEY (id),
                FOREIGN KEY(user_id) REFERENCES users (id),
                CONSTRAINT uq_skill_tree_user_category UNIQUE (user_id, category)
            )
        """)

        op.execute("""
            INSERT INTO skill_trees_old (id, user_id, category, tree_data, generated_at)
            SELECT id, user_id, category, tree_data, generated_at
            FROM skill_trees
        """)

        op.execute("DROP INDEX IF EXISTS ix_skill_trees_user_id")
        op.execute("DROP TABLE skill_trees")
        op.execute("ALTER TABLE skill_trees_old RENAME TO skill_trees")
        op.create_index(
            "ix_skill_trees_user_id", "skill_trees", ["user_id"], unique=False
        )
