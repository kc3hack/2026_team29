"""
スキルツリー生成の動作確認スクリプト

GitHub APIとLLM APIを使用して、実際にスキルツリーを生成し、
完了済みノードを含む全体の結果を表示します。

実行方法:
    cd backend
    poetry run python scripts/test_skill_tree_generation.py

環境変数:
    - OPENAI_API_KEY または ANTHROPIC_API_KEY が必要
    - LLM_PROVIDER で使用するLLMを指定（デフォルト: openai）
    - GITHUB_API_TOKEN を設定するとPrivateリポジトリも分析可能
      （未設定の場合はPublicリポジトリのみ、Rate Limit: 60 req/hour）

GitHub API Token の取得方法:
    1. https://github.com/settings/tokens にアクセス
    2. "Generate new token (classic)" を選択
    3. スコープ: repo, read:user, user:email を選択
    4. 生成されたトークンを環境変数に設定:
       export GITHUB_API_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
"""

import asyncio
import json
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.user import User
from app.models.profile import Profile
from app.models.enums import SkillCategory
from app.crud.skill_tree import initialize_skill_trees_for_user
from app.services.skill_tree_service import generate_skill_tree_ai
from app.core.config import settings


# インメモリSQLiteを使用
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def print_separator(char="=", length=70):
    """セパレーターを出力"""
    print(char * length)


def print_node_details(node: dict, indent: int = 2):
    """ノードの詳細を整形して出力"""
    prefix = " " * indent
    print(f"{prefix}📌 {node.get('name', node.get('id'))}")
    print(f"{prefix}   ID: {node.get('id')}")
    print(f"{prefix}   完了: {'✅ 済' if node.get('completed', False) else '⬜️ 未'}")
    if node.get("description"):
        print(f"{prefix}   説明: {node.get('description')}")
    if node.get("estimated_hours"):
        print(f"{prefix}   推定時間: {node.get('estimated_hours')}時間")
    if node.get("prerequisites"):
        print(f"{prefix}   前提条件: {', '.join(node.get('prerequisites', []))}")


async def test_skill_tree_generation(
    github_username: str, categories: list[str] | None = None
):
    """
    スキルツリー生成をテスト

    Args:
        github_username: GitHubユーザー名
        categories: テストするカテゴリのリスト（Noneの場合は全カテゴリ）
    """
    # APIキーチェック
    if settings.LLM_PROVIDER.lower() == "openai":
        if not settings.OPENAI_API_KEY or "REPLACE" in settings.OPENAI_API_KEY:
            print(
                "❌ OPENAI_API_KEY が設定されていません。.envファイルを確認してください。"
            )
            return
    elif settings.LLM_PROVIDER.lower() == "anthropic":
        if not settings.ANTHROPIC_API_KEY or "REPLACE" in settings.ANTHROPIC_API_KEY:
            print(
                "❌ ANTHROPIC_API_KEY が設定されていません。.envファイルを確認してください。"
            )
            return

    # GitHub API Token チェック
    if settings.GITHUB_API_TOKEN:
        print(f"\n✅ GitHub API Token: 設定済み ({settings.GITHUB_API_TOKEN[:10]}...)")
        print("   → Privateリポジトリも分析可能")
        print("   → Rate Limit: 5000 requests/hour")
    else:
        print("\n⚠️  GitHub API Token: 未設定")
        print("   → Publicリポジトリのみ分析可能")
        print("   → Rate Limit: 60 requests/hour")
        print("\n   Privateリポジトリを分析する場合:")
        print("   1. https://github.com/settings/tokens でトークン作成")
        print("   2. スコープ: repo, read:user, user:email を選択")
        print("   3. export GITHUB_API_TOKEN=<your_token> で設定")
        print()

    # DB初期化
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # テストユーザー作成
        print("\n🔧 テストユーザーを作成中...")
        test_user = User(username=f"test_{github_username}", rank=3)
        db.add(test_user)
        db.flush()

        test_profile = Profile(
            user_id=test_user.id,
            github_username=github_username,
            qiita_id="",
        )
        db.add(test_profile)
        db.commit()

        print(f"✅ ユーザー作成完了: {test_user.username} (ID: {test_user.id})")
        print(f"   GitHub: {github_username}")

        # スキルツリー初期化
        initialize_skill_trees_for_user(db, test_user.id)
        print("✅ スキルツリー初期化完了")

        # カテゴリリスト
        if categories is None:
            categories = [cat.value for cat in SkillCategory]

        print("\n🌳 スキルツリー生成を開始します...")
        print(f"対象カテゴリ: {', '.join(categories)}")
        print(f"LLMプロバイダー: {settings.LLM_PROVIDER}")
        print()

        # 各カテゴリでスキルツリー生成
        for category_name in categories:
            try:
                category = SkillCategory(category_name)
            except ValueError:
                print(f"⚠️  無効なカテゴリ: {category_name}")
                continue

            print_separator()
            print(f"📂 カテゴリ: {category_name.upper()}")
            print_separator()

            # スキルツリー生成
            print("\n🔄 生成中... (GitHub API + LLM API呼び出し)")

            # GitHub分析結果を確認
            from app.services.github_service import analyze_github_profile

            github_analysis = await analyze_github_profile(github_username)
            print("\n📊 GitHub分析結果:")
            print(
                f"   言語: {', '.join(github_analysis.get('languages', [])) or 'なし'}"
            )
            print(
                f"   技術スタック: {', '.join(github_analysis.get('tech_stack', [])) or 'なし'}"
            )
            print(f"   リポジトリ数: {github_analysis.get('repo_count', 0)}")
            completion_signals = github_analysis.get("completion_signals", {})
            print(f"   完了シグナル: {len(completion_signals)}個")
            if completion_signals:
                print(
                    f"   完了スキルID: {', '.join(list(completion_signals.keys())[:10])}"
                )

            result = await generate_skill_tree_ai(test_user.id, category, db)

            tree_data = result.tree_data

            # 統計情報
            total_nodes = len(tree_data.get("nodes", []))
            completed_nodes = [
                n for n in tree_data.get("nodes", []) if n.get("completed", False)
            ]
            completed_count = len(completed_nodes)
            progress = tree_data.get("metadata", {}).get("progress_percentage", 0)

            print("✅ 生成完了")
            print("\n📊 統計:")
            print(f"   総ノード数: {total_nodes}")
            print(f"   完了ノード数: {completed_count}")
            print(f"   進捗率: {progress:.1f}%")
            print(f"   生成日時: {result.generated_at}")

            # 完了済みノード表示
            if completed_nodes:
                print(f"\n✅ 完了済みスキル ({len(completed_nodes)}個):")
                for node in completed_nodes:
                    print_node_details(node, indent=2)

            # 未完了ノード（推奨）表示
            next_recommended = tree_data.get("metadata", {}).get("next_recommended", [])
            if next_recommended:
                print(f"\n🎯 次におすすめのスキル ({len(next_recommended)}個):")
                for node_id in next_recommended[:3]:  # 最初の3個だけ
                    node = next(
                        (
                            n
                            for n in tree_data.get("nodes", [])
                            if n.get("id") == node_id
                        ),
                        None,
                    )
                    if node:
                        print_node_details(node, indent=2)

            # 全ノード表示（オプション）
            print("\n📋 全ノード一覧:")
            for i, node in enumerate(tree_data.get("nodes", []), 1):
                status = "✅" if node.get("completed", False) else "⬜️"
                print(f"   {i:2d}. {status} {node.get('name', node.get('id'))}")

            # エッジ（依存関係）表示
            edges = tree_data.get("edges", [])
            if edges:
                print(f"\n🔗 依存関係 ({len(edges)}個):")
                for edge in edges[:10]:  # 最初の10個だけ
                    print(f"   {edge.get('from')} → {edge.get('to')}")
                if len(edges) > 10:
                    print(f"   ... 他 {len(edges) - 10} 個")

            # JSON保存（オプション）
            output_file = (
                Path(__file__).parent
                / f"skill_tree_{category_name}_{github_username}.json"
            )
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(tree_data, f, ensure_ascii=False, indent=2)
            print(f"\n💾 JSONを保存: {output_file}")

            print()

        print_separator()
        print("🎉 全てのスキルツリー生成が完了しました!")
        print_separator()

    except Exception as e:
        print(f"\n❌ エラー発生: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


def main():
    """メイン関数"""
    print_separator("=", 70)
    print("🌳 スキルツリー生成テストスクリプト")
    print_separator("=", 70)

    # コマンドライン引数からGitHubユーザー名を取得
    if len(sys.argv) > 1:
        github_username = sys.argv[1]
    else:
        # デフォルトはユーザー入力
        print("\nGitHubユーザー名を入力してください:")
        github_username = input(">>> ").strip()

    if not github_username:
        print("❌ GitHubユーザー名が入力されていません。")
        return

    # カテゴリ指定（オプション）
    categories = None
    if len(sys.argv) > 2:
        categories = sys.argv[2].split(",")

    # 実行
    asyncio.run(test_skill_tree_generation(github_username, categories))


if __name__ == "__main__":
    main()
