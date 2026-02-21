"""ストリーミング動作テスト

バックエンドのSSEエンドポイントをテストする簡易スクリプト
"""

import asyncio
import json
from app.core.llm import stream_llm
from app.core.prompts_streaming import SKILL_TREE_STREAMING_TEMPLATE


async def test_streaming():
    """ストリーミングテスト: JSON Lines形式でノード単位に出力"""
    print("=" * 80)
    print("スキルツリー ストリーミング生成テスト")
    print("=" * 80)

    # モックユーザー情報
    user_info = {
        "rank": 5,
        "rank_name": "林",
        "github_username": "test_user",
        "tech_stack": "FastAPI, Next.js, PostgreSQL, Docker",
        "acquired_skills": "python, javascript, typescript, fastapi, nextjs",
        "category": "web",
    }

    # ベースライン簡略化（2ノードのみ）
    baseline_json = json.dumps(
        [
            {
                "id": "html-css",
                "name": "HTML/CSS基礎",
                "description": "Webページの構造とスタイリング...",
                "prerequisites": [],
                "estimated_hours": 20,
            },
            {
                "id": "javascript",
                "name": "JavaScript基礎",
                "description": "Webの動的な動作を実装...",
                "prerequisites": ["html-css"],
                "estimated_hours": 30,
            },
        ],
        ensure_ascii=False,
    )

    # プロンプト生成
    prompt = SKILL_TREE_STREAMING_TEMPLATE.format(
        rank=user_info["rank"],
        rank_name=user_info["rank_name"],
        github_username=user_info["github_username"],
        tech_stack=user_info["tech_stack"],
        acquired_skills=user_info["acquired_skills"],
        category=user_info["category"],
        baseline_json=baseline_json,
    )

    print("\n📝 プロンプト送信:")
    print(f"   カテゴリ: {user_info['category']}")
    print(f"   ランク: {user_info['rank']} ({user_info['rank_name']})")
    print(f"   プロンプト長: {len(prompt)} 文字")

    print("\n🤖 ストリーミング開始...")
    print("-" * 80)

    node_count = 0
    buffer = ""

    try:
        async for chunk in stream_llm(prompt, temperature=0.1):
            buffer += chunk

            # 改行ごとにJSON Linesをパース
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                try:
                    data = json.loads(line)
                    data_type = data.get("type")

                    if data_type == "node":
                        node_count += 1
                        print(
                            f"✅ ノード {node_count}: {data['name']} (prerequisites: {data.get('prerequisites', [])})"
                        )
                    elif data_type == "edge":
                        print(f"🔗 エッジ: {data.get('from')} → {data.get('to')}")
                    elif data_type == "metadata":
                        print("\n📊 メタデータ:")
                        print(f"   - 総ノード数: {data.get('total_nodes')}")
                        print(f"   - 完了ノード数: {data.get('completed_nodes')}")
                        print(f"   - 進捗率: {data.get('progress_percentage')}%")

                except json.JSONDecodeError as e:
                    print(f"⚠️  JSON パースエラー: {e}")
                    print(f"   行: {line[:60]}...")
                    continue

        # 残りバッファをチェック
        if buffer.strip():
            try:
                data = json.loads(buffer.strip())
                data_type = data.get("type")
                if data_type == "node":
                    node_count += 1
                    print(
                        f"✅ ノード {node_count}: {data['name']} (prerequisites: {data.get('prerequisites', [])})"
                    )
            except json.JSONDecodeError:
                pass

        print("-" * 80)
        print("\n🎉 ストリーミング完了!")
        print(f"   - 受信ノード数: {node_count}")

        # 順序検証
        print("\n🔍 順序検証:")
        if node_count >= 3:
            print("   ✅ 複数ノード受信 → 依存関係順序を確認してください")
        else:
            print("   ⚠️  ノード数が少ないため順序検証不可")

        return True

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_streaming())
    exit(0 if success else 1)
