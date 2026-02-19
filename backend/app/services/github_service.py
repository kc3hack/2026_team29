"""
GitHub API統合サービス

ユーザーのGitHubプロフィールを分析し、技術スタックと習得済みスキルを推定する。
"""

import json
import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# Rate Limitやエラー時のデフォルト値
DEFAULT_GITHUB_ANALYSIS = {
    "languages": [],
    "repo_count": 0,
    "tech_stack": [],
    "recent_activity": "データ取得できませんでした",
    "completion_signals": {},
}


async def analyze_github_profile(username: str | None) -> dict[str, Any]:
    """
    GitHub APIでユーザープロフィールを分析

    Args:
        username: GitHubユーザー名（Noneの場合はデフォルト値を返却）

    Returns:
        {
            "languages": ["Python", "JavaScript", "TypeScript"],
            "repo_count": 42,
            "tech_stack": ["FastAPI", "React", "Docker"],
            "recent_activity": "過去30日で15コミット",
            "completion_signals": {
                "html-css": True,
                "js-basics": True,
                "python-basics": True,
                ...
            }
        }

    Raises:
        HTTPException: GitHub API呼び出しが失敗した場合
    """
    if not username:
        logger.warning("GitHub username is None, returning default analysis")
        return DEFAULT_GITHUB_ANALYSIS

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # ユーザー情報取得
            user_response = await client.get(
                f"https://api.github.com/users/{username}",
                headers=_get_github_headers(),
            )

            if user_response.status_code == 404:
                logger.warning(f"GitHub user not found: {username}")
                return DEFAULT_GITHUB_ANALYSIS

            if user_response.status_code == 403:
                logger.error("GitHub API rate limit exceeded")
                return DEFAULT_GITHUB_ANALYSIS

            user_response.raise_for_status()
            user_data = user_response.json()

            # リポジトリ一覧取得（最大100件）
            repos_response = await client.get(
                f"https://api.github.com/users/{username}/repos",
                params={"sort": "updated", "per_page": 100},
                headers=_get_github_headers(),
            )
            repos_response.raise_for_status()
            repos = repos_response.json()

            # 言語分析
            languages = _analyze_languages(repos)

            # 技術スタック検出
            tech_stack = await _detect_tech_stack(client, username, repos)

            # 最近の活動（簡易版）
            recent_activity = _analyze_recent_activity(user_data, repos)

            # スキル完了シグナル
            completion_signals = _generate_completion_signals(languages, tech_stack)

            return {
                "languages": languages,
                "repo_count": len(repos),
                "tech_stack": tech_stack,
                "recent_activity": recent_activity,
                "completion_signals": completion_signals,
            }

    except httpx.TimeoutException:
        logger.error(f"GitHub API timeout for user: {username}")
        return DEFAULT_GITHUB_ANALYSIS
    except httpx.HTTPError as e:
        logger.error(f"GitHub API error for user {username}: {e}")
        return DEFAULT_GITHUB_ANALYSIS
    except Exception as e:
        logger.error(f"Unexpected error analyzing GitHub profile for {username}: {e}")
        return DEFAULT_GITHUB_ANALYSIS


def _get_github_headers() -> dict[str, str]:
    """GitHub API リクエストヘッダーを生成"""
    headers = {"Accept": "application/vnd.github.v3+json"}

    # GITHUB_API_TOKENが設定されている場合は使用
    if hasattr(settings, "GITHUB_API_TOKEN") and settings.GITHUB_API_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_API_TOKEN}"

    return headers


def _analyze_languages(repos: list[dict[str, Any]]) -> list[str]:
    """
    リポジトリから使用言語を集計

    Args:
        repos: GitHub API /users/{username}/repos のレスポンス

    Returns:
        使用言語のリスト（出現頻度順、最大10件）
    """
    language_count: dict[str, int] = {}

    for repo in repos:
        lang = repo.get("language")
        if lang:
            language_count[lang] = language_count.get(lang, 0) + 1

    # 出現頻度順にソート
    sorted_languages = sorted(language_count.items(), key=lambda x: x[1], reverse=True)

    return [lang for lang, _ in sorted_languages[:10]]


async def _detect_tech_stack(
    client: httpx.AsyncClient, username: str, repos: list[dict[str, Any]]
) -> list[str]:
    """
    特定の技術スタック（フレームワーク、ツール）を検出

    Args:
        client: httpx AsyncClient
        username: GitHubユーザー名
        repos: リポジトリリスト

    Returns:
        検出された技術スタックのリスト
    """
    tech_stack = set()

    # 主要リポジトリ（スター数順、最大10件）から検出
    sorted_repos = sorted(
        repos, key=lambda r: r.get("stargazers_count", 0), reverse=True
    )[:10]

    for repo in sorted_repos:
        repo_name = repo.get("name", "")
        description = repo.get("description", "") or ""

        # リポジトリ名・説明文から技術スタックを推定
        tech_keywords = {
            "FastAPI": ["fastapi"],
            "Django": ["django"],
            "Flask": ["flask"],
            "React": ["react", "reactjs"],
            "Next.js": ["nextjs", "next.js"],
            "Vue": ["vue", "vuejs"],
            "Angular": ["angular"],
            "TypeScript": ["typescript", "ts"],
            "Docker": ["docker", "dockerfile"],
            "Kubernetes": ["kubernetes", "k8s"],
            "TensorFlow": ["tensorflow"],
            "PyTorch": ["pytorch"],
            "Scikit-learn": ["scikit", "sklearn"],
        }

        combined_text = f"{repo_name} {description}".lower()

        for tech, keywords in tech_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                tech_stack.add(tech)

    return sorted(list(tech_stack))


def _analyze_recent_activity(
    user_data: dict[str, Any], repos: list[dict[str, Any]]
) -> str:
    """
    最近の活動状況を要約

    Args:
        user_data: GitHub API /users/{username} のレスポンス
        repos: リポジトリリスト

    Returns:
        活動状況のテキスト
    """
    public_repos = user_data.get("public_repos", 0)

    # 最近更新されたリポジトリの数（30日以内）
    from datetime import UTC, datetime, timedelta

    thirty_days_ago = datetime.now(UTC) - timedelta(days=30)
    recent_repos = 0

    for repo in repos:
        updated_at_str = repo.get("updated_at")
        if updated_at_str:
            try:
                updated_at = datetime.fromisoformat(
                    updated_at_str.replace("Z", "+00:00")
                )
                if updated_at > thirty_days_ago:
                    recent_repos += 1
            except ValueError:
                continue

    if recent_repos > 0:
        return f"公開リポジトリ{public_repos}件、過去30日で{recent_repos}件を更新"
    else:
        return f"公開リポジトリ{public_repos}件"


def _generate_completion_signals(
    languages: list[str], tech_stack: list[str]
) -> dict[str, bool]:
    """
    習得済みスキルのシグナルを生成

    Args:
        languages: 使用言語リスト
        tech_stack: 技術スタックリスト

    Returns:
        スキルID: 完了フラグのマッピング
    """
    signals = {}

    # 言語ベースのシグナル
    language_mapping = {
        "HTML": ["web_html_css"],
        "CSS": ["web_html_css"],
        "JavaScript": ["web_js_basics"],
        "TypeScript": ["web_typescript"],
        "Python": ["ai_python_basics", "infrastructure_linux_basics"],
        "Java": ["infrastructure_container"],
        "Go": ["infrastructure_container"],
        "Rust": ["infrastructure_container"],
        "C": ["game_math"],
        "C++": ["game_math", "game_engine"],
        "C#": ["game_engine"],
    }

    for lang in languages:
        if lang in language_mapping:
            for skill_id in language_mapping[lang]:
                signals[skill_id] = True

    # 技術スタックベースのシグナル
    tech_mapping = {
        "React": ["web_react"],
        "Next.js": ["web_nextjs"],
        "Vue": ["web_vue"],
        "Angular": ["web_angular"],
        "FastAPI": ["web_api_design"],
        "Django": ["web_api_design"],
        "Flask": ["web_api_design"],
        "Docker": ["infrastructure_docker"],
        "Kubernetes": ["infrastructure_kubernetes"],
        "TensorFlow": ["ai_deep_learning"],
        "PyTorch": ["ai_deep_learning"],
        "Scikit-learn": ["ai_ml"],
    }

    for tech in tech_stack:
        if tech in tech_mapping:
            for skill_id in tech_mapping[tech]:
                signals[skill_id] = True

    return signals
