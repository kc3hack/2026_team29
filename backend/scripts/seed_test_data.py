"""テストデータ投入スクリプト

スキルツリー生成APIの動作確認用にテストユーザーを作成します。

Usage:
    cd backend
    poetry run python scripts/seed_test_data.py
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

# 全モデルを登録するため、base をインポート（重要！）
from app.db import base  # noqa: F401
from app.db.session import SessionLocal
from app.models.user import User
from app.models.profile import Profile
from app.crud import user as crud_user
from app.schemas.user import UserCreate


def seed_test_users():
    """テストユーザーを作成"""
    db = SessionLocal()
    try:
        # 既存のテストユーザーを確認
        existing_users = (
            db.query(User)
            .filter(
                User.username.in_(
                    ["test_beginner", "test_intermediate", "test_advanced"]
                )
            )
            .all()
        )

        if existing_users:
            print(f"⚠️  既に {len(existing_users)} 件のテストユーザーが存在します:")
            for user in existing_users:
                print(f"  - User {user.id}: {user.username} (rank={user.rank})")

            response = input("\n既存データを削除して再作成しますか？ (y/N): ")
            if response.lower() != "y":
                print("キャンセルしました。")
                return

            # 既存データを削除（Profileも自動削除される: cascade設定）
            for user in existing_users:
                db.delete(user)
            db.commit()
            print("既存データを削除しました。\n")

        # User 1: 初心者（rank=2）
        user1 = crud_user.create_user(
            db,
            UserCreate(username="test_beginner", password="testpass123"),
            commit=False,
        )
        user1.rank = 2
        user1.exp = 100
        db.flush()

        profile1 = Profile(
            user_id=user1.id,
            github_username="beginner123",
        )
        db.add(profile1)

        # User 2: 中級者（rank=5）
        user2 = crud_user.create_user(
            db,
            UserCreate(username="test_intermediate", password="testpass123"),
            commit=False,
        )
        user2.rank = 5
        user2.exp = 1000
        db.flush()

        profile2 = Profile(
            user_id=user2.id,
            github_username="Inlet-back",
        )
        db.add(profile2)

        # User 3: 上級者（rank=8）
        user3 = crud_user.create_user(
            db,
            UserCreate(username="test_advanced", password="testpass123"),
            commit=False,
        )
        user3.rank = 8
        user3.exp = 5000
        db.flush()

        profile3 = Profile(
            user_id=user3.id,
            github_username="torvalds",
        )
        db.add(profile3)

        db.commit()

        print("\n" + "=" * 60)
        print("✅ テストユーザー作成完了")
        print("=" * 60)
        print(
            f"\nUser {user1.id}: {user1.username} (rank={user1.rank}) → GitHub: {profile1.github_username}"
        )
        print(
            f"User {user2.id}: {user2.username} (rank={user2.rank}) → GitHub: {profile2.github_username}"
        )
        print(
            f"User {user3.id}: {user3.username} (rank={user3.rank}) → GitHub: {profile3.github_username}"
        )

        print("\n" + "=" * 60)
        print("【機能要件】スキルツリー生成API - Issue #54")
        print("=" * 60)
        print("\n✓ 以下のコマンドで動作確認:")
        print("\n  curl -X POST http://localhost:8000/api/v1/analyze/skill-tree \\")
        print('    -H "Content-Type: application/json" \\')
        print(f'    -d \'{{"user_id": {user1.id}, "category": "web"}}\' | jq')

        print("\n✓ 期待される結果:")
        print("  - HTTPステータス: 200 OK")
        print("  - レスポンス: category, tree_data, generated_at を含むJSON")
        print("  - tree_data.nodes: 20個のスキルノード（web.jsonベースライン）")
        print("  - tree_data.edges: 依存関係グラフ")
        print("  - tree_data.metadata: 進捗率、次の推奨スキル")
        print("  - GitHub分析結果が completed フラグに反映")
        print("  - LLM生成 + GitHub分析のパーソナライズ済みツリー")

        print("\n✓ 全6カテゴリでテスト可能:")
        print('  "web", "ai", "security", "infrastructure", "design", "game"')
        print("\n" + "=" * 60)

    except Exception as e:
        db.rollback()
        print(f"❌ エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("テストデータ投入スクリプト")
    print("=" * 60)
    seed_test_users()
