"""
ランク判定サービス

LLMを使用してユーザーのランクを判定するビジネスロジック
"""

import json
from app.core.llm import invoke_llm
from app.core.prompts import RANK_ANALYSIS_TEMPLATE


async def analyze_user_rank(
    github_username: str,
    portfolio_text: str = "",
    qiita_id: str = "",
    other_info: str = "",
) -> dict:
    """
    LLMを使用してユーザーのランクを判定

    Args:
        github_username: GitHubのユーザー名
        portfolio_text: ポートフォリオ情報
        qiita_id: Qiita ID
        other_info: その他の活動情報

    Returns:
        {
            "percentile": float,
            "rank": int,
            "rank_name": str,
            "reasoning": str
        }

    Note:
        - 現在はユーザー入力の文字列のみで判定（GitHub API統合は後続Issue）
        - JSONパースエラー時はデフォルト値を返す
    """
    # プロンプトテンプレートに入力値を埋め込む
    prompt = RANK_ANALYSIS_TEMPLATE.format(
        github_username=github_username,
        portfolio_text=portfolio_text or "未入力",
        qiita_id=qiita_id or "未入力",
        other_info=other_info or "未入力",
    )

    # LLMに非同期で呼び出し
    response = await invoke_llm(prompt=prompt, temperature=0.2)

    # JSONパース（エラーハンドリング付き）
    try:
        result = json.loads(response)
        # 必須フィールドの存在確認
        if not all(k in result for k in ["percentile", "rank", "rank_name", "reasoning"]):
            raise ValueError("Missing required fields in LLM response")
        return result
    except (json.JSONDecodeError, ValueError) as e:
        # LLMがJSON以外を返した場合のフォールバック
        print(f"JSON parse error: {e}. Returning fallback response.")
        return {
            "percentile": 50.0,
            "rank": 3,
            "rank_name": "巨木",
            "reasoning": "判定結果の解析に失敗したため、デフォルト値を返却しました。",
        }
