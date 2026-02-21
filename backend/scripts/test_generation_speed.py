"""Issue #88: スキルツリー生成速度テスト

Few-shot promptingによる最適化効果を測定
"""

import asyncio
import json
import time

from app.core.llm import get_llm
from app.services.skill_tree_service import (
    _build_skill_tree_prompt,
    _load_baseline_json,
)
from app.models.enums import SkillCategory


class MockProfile:
    """テスト用モックProfile"""

    def __init__(self):
        self.github_username = "test_user"
        self.user = MockUser()


class MockUser:
    """テスト用モックUser"""

    def __init__(self):
        self.rank = 5


async def test_generation_speed():
    """スキルツリー生成速度テスト"""
    print("=" * 80)
    print("スキルツリー生成速度テスト (Few-shot prompting最適化)")
    print("=" * 80)

    # テスト用データ
    profile = MockProfile()
    category = SkillCategory.WEB
    baseline_data = _load_baseline_json(category)

    github_analysis = {
        "languages": ["Python", "JavaScript", "TypeScript"],
        "repo_count": 15,
        "tech_stack": ["FastAPI", "Next.js", "PostgreSQL", "Docker"],
        "recent_activity": "Last commit: 2 days ago",
        "completion_signals": {
            "python": True,
            "javascript": True,
            "typescript": True,
            "fastapi": True,
            "nextjs": True,
            "postgresql": True,
            "docker": True,
        },
    }

    completed_quests = ["FastAPI入門", "Next.js基礎", "Docker環境構築"]

    # プロンプト生成
    print("\n📝 プロンプト生成中...")
    prompt = _build_skill_tree_prompt(
        profile=profile,
        category=category,
        github_analysis=github_analysis,
        completed_quests=completed_quests,
        baseline_data=baseline_data,
    )

    print("\n📊 プロンプト統計:")
    print(f"   - 文字数: {len(prompt):,} 文字")
    print(f"   - 推定トークン数: {len(prompt) // 3:,} tokens (概算)")

    # LLM呼び出し（時間計測）
    print("\n🤖 LLM生成開始...")
    start_time = time.time()

    try:
        llm = get_llm()
        response = await llm.ainvoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)

        elapsed_time = time.time() - start_time

        # JSONパース
        import re

        json_match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = content.strip()

        tree_data = json.loads(json_str)

        # 結果表示
        print("\n✅ 生成完了!")
        print("=" * 80)
        print(f"⏱️  生成時間: {elapsed_time:.2f}秒")
        print("📊 生成結果:")
        print(f"   - ノード数: {tree_data['metadata']['total_nodes']}")
        print(f"   - 完了ノード数: {tree_data['metadata']['completed_nodes']}")
        print(f"   - 進捗率: {tree_data['metadata']['progress_percentage']}%")

        # 速度評価
        print("\n📈 パフォーマンス評価:")
        if elapsed_time < 5:
            print("   🚀 非常に高速! (5秒未満)")
        elif elapsed_time < 10:
            print("   ✅ 高速 (5-10秒)")
        elif elapsed_time < 15:
            print("   ⚠️  やや遅い (10-15秒)")
        else:
            print("   ❌ 遅い (15秒以上)")

        # 最適化効果の推定
        baseline_tokens = len(json.dumps(baseline_data, ensure_ascii=False)) // 3
        optimized_tokens = len(prompt) // 3
        reduction = ((baseline_tokens - optimized_tokens) / baseline_tokens) * 100
        print("\n🔧 最適化効果:")
        print(f"   - ベースライン全体: 約{baseline_tokens:,} tokens")
        print(f"   - Few-shot最適化後: 約{optimized_tokens:,} tokens")
        print(f"   - トークン削減率: {reduction:.1f}%")

        print("\n" + "=" * 80)
        print("🎉 テスト完了!")

        return True

    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ エラー ({elapsed_time:.2f}秒経過): {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_generation_speed())
    exit(0 if success else 1)
