"""
ランク判定サービス

LLMを使用してユーザーのランクを判定するビジネスロジック
"""

import json
from typing import Any

from app.core.config import settings
from app.core.llm import invoke_llm
from app.core.prompts import RANK_ANALYSIS_TEMPLATE, RANK_ANALYSIS_TEMPLATE_GITHUB
from app.models.profile import Profile


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
        if not all(
            k in result for k in ["percentile", "rank", "rank_name", "reasoning"]
        ):
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


async def analyze_user_rank_from_github(
    github_stats: dict[str, Any],
    profile: Profile | None = None,
) -> dict[str, Any]:
    """
    GitHub統計情報を元にランク判定を実行 (Issue #105)

    OAuth完了直後に呼び出され、GitHub APIから取得した統計情報を元に
    LLMでランク判定を実行する。プロフィール情報があれば補足情報として使用。

    Args:
        github_stats: fetch_github_user_stats() の戻り値
            {
                "username": str,
                "public_repos": int,
                "followers": int,
                "following": int,
                "created_at": str,
                "bio": str,
                "languages": dict,
                "total_stars": int,
            }
        profile: ユーザープロフィール（任意）

    Returns:
        {
            "percentile": float,
            "rank": int,
            "rank_name": str,
            "reasoning": str,
            "estimated_exp": int,  # ランクから逆算した経験値（概算）
        }

    Note:
        - LLM呼び出し失敗時はデフォルト値（rank=3: 巨木）を返却
        - estimated_expはランクに応じた経験値の中央値を推定
    """
    # 言語統計をフォーマット
    languages_str = ", ".join(
        f"{lang}({count})" for lang, count in github_stats.get("languages", {}).items()
    )
    if not languages_str:
        languages_str = "不明"

    # プロンプトテンプレートに統計情報を埋め込む
    prompt = RANK_ANALYSIS_TEMPLATE_GITHUB.format(
        github_username=github_stats.get("username", "不明"),
        created_at=github_stats.get("created_at", "不明"),
        public_repos=github_stats.get("public_repos", 0),
        followers=github_stats.get("followers", 0),
        total_stars=github_stats.get("total_stars", 0),
        languages=languages_str,
        bio=github_stats.get("bio", "") or "未入力",
        portfolio_text=profile.portfolio_text if profile else "未入力",
        qiita_id=profile.qiita_id if profile else "未入力",
        other_info=profile.other_info if profile else "未入力",
    )

    # LLM呼び出し
    response = await invoke_llm(prompt=prompt, temperature=0.2)

    # JSONパース（エラーハンドリング付き）
    try:
        result = json.loads(response)
        # 必須フィールドの存在確認
        if not all(
            k in result for k in ["percentile", "rank", "rank_name", "reasoning"]
        ):
            raise ValueError("Missing required fields in LLM response")
        # ランクから経験値を逆算（概算）
        result["estimated_exp"] = estimate_exp_from_rank(result["rank"])
        return result
    except (json.JSONDecodeError, ValueError) as e:
        # LLMがJSON以外を返した場合のフォールバック
        print(f"JSON parse error in GitHub rank analysis: {e}. Returning fallback.")
        return {
            "percentile": 50.0,
            "rank": 3,
            "rank_name": "巨木",
            "estimated_exp": 500,
            "reasoning": "GitHub統計の解析に失敗したため、デフォルト値を設定しました。",
        }


def estimate_exp_from_rank(rank: int) -> int:
    """
    ランクから経験値を逆算（各ランクの中央値を推定）

    Args:
        rank: ランク値（0-9）

    Returns:
        推定経験値（各ランクの中央値）

    Note:
        - settings.RANK_THRESHOLDSを参照して中央値を計算
        - 最高ランクの場合は閾値+500を返す
    """
    if rank >= len(settings.RANK_THRESHOLDS):
        # 最高ランクを超える場合（通常はありえない）
        return settings.RANK_THRESHOLDS[-1] + 500
    if rank == 0:
        # 種子（rank 0）: 閾値0から次の閾値の中央値
        if len(settings.RANK_THRESHOLDS) > 1:
            return settings.RANK_THRESHOLDS[1] // 2
        return 0
    # rank n の中央値 = (閾値 n + 閾値 n+1) / 2
    current_threshold = settings.RANK_THRESHOLDS[rank]
    if rank + 1 < len(settings.RANK_THRESHOLDS):
        next_threshold = settings.RANK_THRESHOLDS[rank + 1]
        return (current_threshold + next_threshold) // 2
    else:
        # 最高ランク: 閾値+500
        return current_threshold + 500
