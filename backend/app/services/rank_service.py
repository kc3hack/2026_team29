"""
ランク判定サービス

LLMを使用してユーザーのランクを判定するビジネスロジック
"""

import json
import logging
import re
from typing import Any

from app.core.config import settings
from app.core.llm import invoke_llm
from app.core.prompts import RANK_ANALYSIS_TEMPLATE, RANK_ANALYSIS_TEMPLATE_GITHUB
from app.models.profile import Profile

logger = logging.getLogger(__name__)


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
        # LLM応答の前後の空白・改行を削除
        cleaned_response = response.strip()

        # Markdownコードブロック（```json ... ``` または ``` ... ```）を除去
        if cleaned_response.startswith("```"):
            cleaned_response = re.sub(r"^```(?:json)?\s*\n", "", cleaned_response)
            cleaned_response = re.sub(r"\n```\s*$", "", cleaned_response)

        result = json.loads(cleaned_response)
        # 必須フィールドの存在確認
        if not all(
            k in result for k in ["percentile", "rank", "rank_name", "reasoning"]
        ):
            raise ValueError("Missing required fields in LLM response")
        return result
    except (json.JSONDecodeError, ValueError) as e:
        # LLMがJSON以外を返した場合のフォールバック
        logger.warning(
            f"JSON parse error: {e}. "
            f"LLM response: {response[:200] if response else '(empty)'}... Returning fallback response."
        )
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
    # Profileからその他の情報を構築
    other_info_parts = []
    if profile:
        if profile.connpass_id:
            other_info_parts.append(f"Connpass: {profile.connpass_id}")
        if profile.portfolio_url:
            other_info_parts.append(f"Portfolio URL: {profile.portfolio_url}")
    other_info = ", ".join(other_info_parts) if other_info_parts else "未入力"

    prompt = RANK_ANALYSIS_TEMPLATE_GITHUB.format(
        github_username=github_stats.get("username", "不明"),
        created_at=github_stats.get("created_at", "不明"),
        public_repos=github_stats.get("public_repos", 0),
        followers=github_stats.get("followers", 0),
        total_stars=github_stats.get("total_stars", 0),
        languages=languages_str,
        bio=github_stats.get("bio", "") or "未入力",
        portfolio_text=(profile.portfolio_text or "未入力") if profile else "未入力",
        qiita_id=(profile.qiita_id or "未入力") if profile else "未入力",
        other_info=other_info,
    )

    # LLM呼び出し
    response = await invoke_llm(prompt=prompt, temperature=0.2)

    # JSONパース（エラーハンドリング付き）
    try:
        # LLM応答の前後の空白・改行を削除
        cleaned_response = response.strip()

        # Markdownコードブロック（```json ... ``` または ``` ... ```）を除去
        # LLMが応答をMarkdownで囲む場合があるため
        if cleaned_response.startswith("```"):
            # 最初の改行までを削除（```json または ``` 部分）
            cleaned_response = re.sub(r"^```(?:json)?\s*\n", "", cleaned_response)
            # 最後の ```を削除
            cleaned_response = re.sub(r"\n```\s*$", "", cleaned_response)

        result = json.loads(cleaned_response)
        # 必須フィールドの存在確認
        if not all(
            k in result for k in ["percentile", "rank", "rank_name", "reasoning"]
        ):
            raise ValueError("Missing required fields in LLM response")
        # ランクから経験値を逆算（概算）
        result["estimated_exp"] = estimate_exp_from_rank(result["rank"])
        logger.info(
            f"GitHub rank analysis successful: rank={result['rank']}, reasoning={result['reasoning'][:100]}..."
        )
        return result
    except (json.JSONDecodeError, ValueError) as e:
        # LLMがJSON以外を返した場合のフォールバック
        logger.warning(
            f"JSON parse error in GitHub rank analysis: {e}. "
            f"LLM response: {response[:200] if response else '(empty)'}... Returning fallback."
        )
        return {
            "percentile": 50.0,
            "rank": 3,
            "rank_name": "巨木",
            "estimated_exp": estimate_exp_from_rank(3),
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
