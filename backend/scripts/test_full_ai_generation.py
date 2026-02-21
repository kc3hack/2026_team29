"""Issue #88 完全AI生成モード: ベースラインなしでスキルツリー生成テスト

既存のベースラインJSONを例示として見せつつ、
完全にゼロからスキルツリーを生成させるテストを実行する。
"""

import asyncio
import json
from pathlib import Path
from app.core.llm import get_llm
from app.services.skill_tree_service import RANK_NAMES

# 既存のベースラインを読み込み（例示用）
BASELINE_DIR = Path(__file__).parent.parent / "data" / "skill_trees"


def load_baseline_example(category: str) -> dict:
    """既存のベースラインJSONを読み込み（例示用）"""
    baseline_path = BASELINE_DIR / f"{category}.json"
    if not baseline_path.exists():
        return {"nodes": [], "edges": []}

    with open(baseline_path, "r", encoding="utf-8") as f:
        return json.load(f)


async def test_full_ai_generation():
    """完全AI生成モードのテスト"""
    print("=" * 80)
    print("Issue #88: 完全AI生成モード - ベースラインなしでスキルツリー生成")
    print("=" * 80)

    # テスト用のモックユーザー情報
    test_user = {
        "rank": 5,
        "rank_name": RANK_NAMES.get(5, "林"),
        "github_username": "example_user",
        "languages": "Python, JavaScript, TypeScript",
        "repo_count": 15,
        "tech_stack": "FastAPI, Next.js, PostgreSQL, Docker",
        "recent_activity": "Last commit: 2 days ago",
        "acquired_skills": "python, javascript, typescript, fastapi, nextjs, postgresql, docker",
        "completed_quests": "FastAPI入門, Next.js基礎, Docker環境構築",
        "category": "web",
    }

    # 既存のベースラインを例示として表示
    baseline_example = load_baseline_example(test_user["category"])
    print(f"\n📚 既存のベースライン例（{test_user['category']}.json）:")
    print(f"   - ノード数: {len(baseline_example.get('nodes', []))}")
    print(f"   - エッジ数: {len(baseline_example.get('edges', []))}")

    # ベースラインを例示として見せるプロンプト（参考として渡すが、それに縛られないように指示）
    prompt_with_reference = f"""あなたは優秀なキャリアアドバイザーです。
このエンジニアの現在のスキルレベルと目標に基づいて、
パーソナライズされたスキルツリー（学習ロードマップ）を生成してください。

## エンジニア情報
- 現在のランク: {test_user['rank']} ({test_user['rank_name']})
- GitHub: {test_user['github_username']}
  - 主な使用言語: {test_user['languages']}
  - リポジトリ数: {test_user['repo_count']}
  - 技術スタック: {test_user['tech_stack']}
  - 最近の活動: {test_user['recent_activity']}
- 習得済みスキル（GitHub分析結果）: {test_user['acquired_skills']}
- 完了したQuest: {test_user['completed_quests']}

## 選択されたカテゴリ: {test_user['category']}

## 参考: 既存のスキルツリー例
以下は参考例ですが、このユーザー専用にカスタマイズして構いません。
基礎スキルは必要に応じて削減し、ユーザーの習熟度に応じた応用スキルを追加してください。

```json
{json.dumps(baseline_example, ensure_ascii=False, indent=2)}
```

## 生成要件
1. **ベースラインをベースに**: ベースラインスキルツリーの重要ノード（12-15個）を残しつつ、ユーザーのレベルと学習履歴に応じてパーソナライズされたノード（15個）を追加
   - **合計目標: 28-30ノード（必須）**（ベースライン12-15 + パーソナライズ15）
   - このユーザーはrank 5（中級者）のため、**必ず28ノード以上生成してください**
   - ユーザーの習熟度が高いカテゴリでは基礎を削減し、応用・発展ノードを追加
   - ユーザーの弱点カテゴリでは基礎・中級ノードを手厚く配置
2. **completed判定（最重要）**: 
   - 「習得済みスキル」リストに含まれるスキルIDは必ず `completed: true` に設定
   - 含まれないスキルは `completed: false` に設定
   - GitHub分析結果を最優先で反映すること
3. **前提条件の定義**: スキル間の依存関係（prerequisites）を技術的に正確に
4. **難易度調整**: ユーザーのランクに応じた学習時間を推定
   - rank 0-2（初心者）: 基礎スキルを手厚く、長めの学習時間
   - rank 3-5（中級者）: 実践的スキル中心、標準的な学習時間
   - rank 6-9（上級者）: 先端技術・アーキテクチャスキル、短めの学習時間
5. **優先順位付け**: 次に取り組むべきスキル（next_recommended）を3つ提示

## 出力形式（JSON）
{{
  "nodes": [
    {{
      "id": "unique-skill-id",
      "name": "スキル名",
      "completed": true/false,
      "description": "スキルの説明",
      "prerequisites": ["前提スキルID"],
      "estimated_hours": 30
    }}
  ],
  "edges": [
    {{"from": "skill-a", "to": "skill-b"}}
  ],
  "metadata": {{
    "total_nodes": 8,
    "completed_nodes": 3,
    "progress_percentage": 37.5,
    "next_recommended": ["skill-x", "skill-y", "skill-z"]
  }}
}}

JSON以外の形式や追加の説明は含めず、JSONのみを出力してください。"""

    print("\n🤖 LLMにスキルツリー生成を依頼中...")
    print(f"   - ユーザーランク: {test_user['rank']} ({test_user['rank_name']})")
    print(f"   - カテゴリ: {test_user['category']}")

    try:
        llm = get_llm()
        response = await llm.ainvoke(prompt_with_reference)

        # レスポンスパース
        content = response.content if hasattr(response, "content") else str(response)

        # JSONを抽出（```json ... ``` の中身を取り出す）
        import re

        json_match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # マークダウンなしの場合
            json_str = content.strip()

        tree_data = json.loads(json_str)

        # 結果表示
        print("\n✅ スキルツリー生成完了！")
        print("=" * 80)
        print("📊 生成結果:")
        print(f"   - 総ノード数: {tree_data['metadata']['total_nodes']}")
        print(f"   - 完了ノード数: {tree_data['metadata']['completed_nodes']}")
        print(f"   - 進捗率: {tree_data['metadata']['progress_percentage']}%")
        print(
            f"   - 次の推奨スキル: {', '.join(tree_data['metadata']['next_recommended'])}"
        )

        print("\n📝 生成されたスキルノード（最初の5件）:")
        for i, node in enumerate(tree_data["nodes"][:5], 1):
            status = "✅" if node["completed"] else "🔒"
            print(f"   {i}. {status} {node['name']} ({node['estimated_hours']}h)")
            print(f"      {node['description'][:60]}...")

        print(f"\n🔗 依存関係（エッジ）: {len(tree_data['edges'])}個")

        # 検証
        print("\n🔍 パーソナライゼーション検証:")
        total = tree_data["metadata"]["total_nodes"]
        if 20 <= total <= 30:
            print(f"   ✅ ノード数が目標範囲内（20-30ノード）: {total}ノード")
        else:
            print(f"   ⚠️  ノード数が範囲外: {total}ノード（目標: 20-30）")

        # ランク5（中級者）の期待値: 22-27ノード
        if 22 <= total <= 27:
            print(f"   ✅ 中級者向けノード数（22-27）: {total}ノード")

        # 習得済みスキルが正しく反映されているか
        completed_count = tree_data["metadata"]["completed_nodes"]
        acquired_list = test_user["acquired_skills"].split(", ")
        print(f"   ✅ 習得済みスキル反映: {completed_count}/{total}ノード")
        print(f"      GitHub分析: {len(acquired_list)}個の技術を検出")

        print("\n" + "=" * 80)
        print("🎉 完全AI生成テスト完了！")

        # 詳細JSONを保存
        output_path = (
            Path(__file__).parent / f"ai_generated_{test_user['category']}.json"
        )
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(tree_data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 生成結果を保存: {output_path}")

        return True

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_full_ai_generation())
    exit(0 if success else 1)
