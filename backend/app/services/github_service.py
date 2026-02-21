"""
GitHub API統合サービス

ユーザーのGitHubプロフィールを分析し、技術スタックと習得済みスキルを推定する。
"""

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
            headers = _get_github_headers()
            is_authenticated = "Authorization" in headers

            # 認証されている場合、認証ユーザー情報を取得
            authenticated_username = None
            if is_authenticated:
                try:
                    auth_user_response = await client.get(
                        "https://api.github.com/user",
                        headers=headers,
                    )
                    if auth_user_response.status_code == 200:
                        authenticated_username = auth_user_response.json().get("login")
                        logger.info(f"Authenticated as: {authenticated_username}")
                except Exception as e:
                    logger.warning(f"Failed to get authenticated user info: {e}")

            # ユーザー情報取得
            user_response = await client.get(
                f"https://api.github.com/users/{username}",
                headers=headers,
            )

            if user_response.status_code == 404:
                logger.warning(f"GitHub user not found: {username}")
                return DEFAULT_GITHUB_ANALYSIS

            if user_response.status_code == 403:
                logger.error("GitHub API rate limit exceeded")
                return DEFAULT_GITHUB_ANALYSIS

            user_response.raise_for_status()
            user_data = user_response.json()

            # リポジトリ一覧取得
            # 認証ユーザーと一致する場合はプライベートリポジトリも取得
            if (
                is_authenticated
                and authenticated_username
                and authenticated_username.lower() == username.lower()
            ):
                logger.info(
                    f"Fetching private repos for authenticated user: {username}"
                )
                repos_response = await client.get(
                    "https://api.github.com/user/repos",
                    params={
                        "affiliation": "owner",
                        "visibility": "all",
                        "sort": "updated",
                        "per_page": 100,
                    },
                    headers=headers,
                )
            else:
                logger.info(f"Fetching public repos only for user: {username}")
                repos_response = await client.get(
                    f"https://api.github.com/users/{username}/repos",
                    params={"sort": "updated", "per_page": 100},
                    headers=headers,
                )

            repos_response.raise_for_status()
            repos = repos_response.json()

            logger.info(f"Fetched {len(repos)} repositories for {username}")

            # 言語分析
            languages = _analyze_languages(repos)
            logger.info(f"Detected languages: {languages}")

            # 技術スタック検出
            tech_stack = await _detect_tech_stack(client, username, repos)
            logger.info(f"Detected tech stack: {tech_stack}")

            # 最近の活動（簡易版）
            recent_activity = _analyze_recent_activity(user_data, repos)

            # スキル完了シグナル
            completion_signals = _generate_completion_signals(
                languages, tech_stack, repos
            )
            logger.info(
                f"Generated {len(completion_signals)} completion signals: {list(completion_signals.keys())}"
            )

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

    # 主要リポジトリ（更新日時順、最大20件）から検出
    sorted_repos = sorted(repos, key=lambda r: r.get("updated_at", ""), reverse=True)[
        :20
    ]

    for repo in sorted_repos:
        repo_name = repo.get("name", "")
        description = repo.get("description", "") or ""
        language = repo.get("language", "") or ""

        # リポジトリ名・説明文・言語から技術スタックを推定
        tech_keywords = {
            # Web Backend
            "FastAPI": ["fastapi", "fast-api"],
            "Django": ["django"],
            "Flask": ["flask"],
            "Express": ["express", "expressjs"],
            "NestJS": ["nestjs"],
            # Web Frontend
            "React": ["react", "reactjs"],
            "Next.js": ["nextjs", "next.js", "next-js"],
            "Vue": ["vue", "vuejs"],
            "Nuxt": ["nuxt", "nuxtjs"],
            "Angular": ["angular"],
            "Svelte": ["svelte"],
            # CSS/UI
            "Tailwind": ["tailwind"],
            "Bootstrap": ["bootstrap"],
            "Material-UI": ["material-ui", "mui"],
            # TypeScript
            "TypeScript": ["typescript"],
            # Infrastructure
            "Docker": ["docker", "dockerfile", "container"],
            "Kubernetes": ["kubernetes", "k8s"],
            "AWS": ["aws", "lambda", "ec2", "s3"],
            "GCP": ["gcp", "google cloud"],
            "Terraform": ["terraform"],
            # Database
            "PostgreSQL": ["postgres", "postgresql"],
            "MySQL": ["mysql"],
            "MongoDB": ["mongodb", "mongo"],
            "Redis": ["redis"],
            # AI/ML
            "TensorFlow": ["tensorflow"],
            "PyTorch": ["pytorch"],
            "Scikit-learn": ["scikit", "sklearn"],
            "Keras": ["keras"],
            "OpenAI": ["openai", "gpt"],
            # Testing
            "Jest": ["jest"],
            "Pytest": ["pytest"],
            "Vitest": ["vitest"],
        }

        combined_text = f"{repo_name} {description} {language}".lower()

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
    languages: list[str], tech_stack: list[str], repos: list[dict[str, Any]]
) -> dict[str, bool]:
    """
    習得済みスキルのシグナルを生成

    Args:
        languages: 使用言語リスト
        tech_stack: 技術スタックリスト
        repos: リポジトリリスト

    Returns:
        スキルID: 完了フラグのマッピング
    """
    signals = {}

    # 言語ベースのシグナル（大幅に拡張）
    language_mapping = {
        "HTML": ["web_html_css", "web_a11y_basics"],
        "CSS": ["web_html_css", "web_css_fw"],
        "JavaScript": ["web_js_basics", "web_js_advanced"],
        "TypeScript": ["web_typescript", "web_js_advanced"],
        "Python": ["ai_python_basics", "ai_data_processing", "infra_shell_scripting"],
        "Java": ["infra_virt_basics"],
        "Go": ["infra_docker", "infra_kubernetes"],
        "Rust": ["infra_linux_admin"],
        "C": ["game_math_basics", "game_physics_basics"],
        "C++": ["game_math_basics", "game_engine_basics"],
        "C#": ["game_engine_basics", "game_scripting"],
        "Ruby": ["web_backend_api"],
        "PHP": ["web_backend_api"],
        "Shell": ["infra_shell_scripting", "infra_linux_admin"],
        "Dockerfile": ["infra_docker"],
    }

    for lang in languages:
        if lang in language_mapping:
            for skill_id in language_mapping[lang]:
                signals[skill_id] = True

    # 技術スタックベースのシグナル（大幅に拡張）
    tech_mapping = {
        # Web Frontend
        "React": ["web_spa_fw", "web_js_advanced"],
        "Next.js": ["web_ssr_ssg", "web_spa_fw", "web_build_tools"],
        "Vue": ["web_spa_fw"],
        "Nuxt": ["web_ssr_ssg", "web_spa_fw"],
        "Angular": ["web_spa_fw"],
        "Svelte": ["web_spa_fw"],
        # Web Backend
        "FastAPI": ["web_backend_api", "web_http_basics"],
        "Django": ["web_backend_api", "web_db_orm"],
        "Flask": ["web_backend_api"],
        "Express": ["web_backend_api"],
        "NestJS": ["web_backend_api"],
        # CSS/UI
        "Tailwind": ["web_css_fw"],
        "Bootstrap": ["web_css_fw"],
        "Material-UI": ["web_css_fw"],
        # Infrastructure
        "Docker": ["infra_docker", "infra_virt_basics"],
        "Kubernetes": ["infra_kubernetes", "infra_docker"],
        "AWS": ["infra_cloud", "infra_cicd"],
        "GCP": ["infra_cloud"],
        "Terraform": ["infra_iac", "infra_cloud"],
        # Database
        "PostgreSQL": ["web_db_orm"],
        "MySQL": ["web_db_orm"],
        "MongoDB": ["web_db_orm"],
        "Redis": ["web_cache"],
        # AI/ML
        "TensorFlow": ["ai_deep_learning", "ai_ml_basics"],
        "PyTorch": ["ai_deep_learning", "ai_ml_basics"],
        "Scikit-learn": ["ai_ml_basics", "ai_statistics"],
        "Keras": ["ai_deep_learning"],
        "OpenAI": ["ai_llm", "ai_ml_basics"],
        # Testing
        "Jest": ["web_testing"],
        "Pytest": ["ai_python_basics"],
        "Vitest": ["web_testing"],
    }

    for tech in tech_stack:
        if tech in tech_mapping:
            for skill_id in tech_mapping[tech]:
                signals[skill_id] = True

    # リポジトリ名・説明からセキュリティ関連を検出
    security_keywords = [
        "security",
        "vulnerability",
        "pentest",
        "penetration",
        "ctf",
        "exploit",
        "hacking",
        "cryptography",
        "crypto",
        "ssl",
        "tls",
        "authentication",
        "authorization",
        "oauth",
        "jwt",
        "xss",
        "csrf",
        "sql injection",
        "injection",
        "firewall",
        "ids",
        "ips",
        "siem",
        "malware",
        "reverse",
        "forensics",
        "audit",
        "compliance",
    ]

    has_security_work = False
    for repo in repos:
        repo_name = repo.get("name", "").lower()
        description = (repo.get("description") or "").lower()
        combined = f"{repo_name} {description}"

        if any(keyword in combined for keyword in security_keywords):
            has_security_work = True
            break

    if has_security_work:
        signals["sec_net_os_basics"] = True
        signals["sec_web_vuln_basics"] = True
        logger.info("Security-related work detected in repositories")

    # HTTPサーバー・API開発の形跡があればHTTP基礎はクリア
    if any(tech in tech_stack for tech in ["FastAPI", "Django", "Flask"]):
        signals["web_http_basics"] = True

    # フロントエンド + バックエンドの両方があれば全体的な理解があると判断
    has_frontend = any(
        tech in tech_stack for tech in ["React", "Next.js", "Vue", "Angular"]
    )
    has_backend = any(tech in tech_stack for tech in ["FastAPI", "Django", "Flask"])

    if has_frontend and has_backend:
        signals["web_build_tools"] = True

    # Dockerがあればインフラ基礎もクリア
    if "Docker" in tech_stack:
        signals["infra_linux_admin"] = True
        signals["infra_net_routing"] = True

    return signals
