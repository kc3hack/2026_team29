"""スキルツリーキャッシュクリアスクリプト

DBに保存されているスキルツリーキャッシュを削除して、
次回アクセス時に最新のプロンプトで再生成させる。
"""

from sqlalchemy import create_engine, text
from app.core.config import settings


def clear_skill_tree_cache(category: str = None):
    """スキルツリーキャッシュを削除

    Args:
        category: 削除するカテゴリ (None の場合は全削除)
    """
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        if category:
            result = conn.execute(
                text("DELETE FROM skill_trees WHERE category = :category"),
                {"category": category},
            )
            conn.commit()
            print(
                f"✅ {category} カテゴリのキャッシュを削除しました（削除件数: {result.rowcount}）"
            )
        else:
            result = conn.execute(text("DELETE FROM skill_trees"))
            conn.commit()
            print(
                f"✅ 全カテゴリのキャッシュを削除しました（削除件数: {result.rowcount}）"
            )

        # 確認
        count = conn.execute(text("SELECT COUNT(*) FROM skill_trees")).scalar()
        print(f"📊 残りのキャッシュ件数: {count}")


if __name__ == "__main__":
    import sys

    category = sys.argv[1] if len(sys.argv) > 1 else None

    if category:
        print(f"🗑️  {category} カテゴリのスキルツリーキャッシュを削除します...")
    else:
        print("🗑️  全カテゴリのスキルツリーキャッシュを削除します...")

    clear_skill_tree_cache(category)

    print("\n✨ 次回アクセス時に新しいプロンプトで再生成されます")
