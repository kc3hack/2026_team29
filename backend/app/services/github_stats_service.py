"""
GitHub OAuth統計情報取得サービス (Issue #105)

GitHub OAuthのアクセストークンを使用して、ユーザーの統計情報を取得する。
ランク判定に必要な客観的データ（リポジトリ数、言語統計、スター数など）を提供。

Note:
  - 既存のgithub_service.pyとは役割が異なる:
    - github_service: 公開情報からスキルツリー生成用の分析を実行
    - github_stats_service (本ファイル): OAuth認証時専用、アクセストークンでランク判定用の統計取得
"""

import logging
from typing import Any

import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)


async def fetch_github_user_stats(access_token: str) -> dict[str, Any]:
    """
    GitHub APIからユーザーの統計情報を取得（OAuth認証済み）

    OAuth完了直後に呼び出され、アクセストークンを使用してユーザー情報を取得する。
    取得したデータはLLMによるランク判定に使用される。

    Args:
        access_token: GitHub OAuthアクセストークン

    Returns:
        {
            "username": str,           # GitHubユーザー名
            "public_repos": int,       # 公開リポジトリ数
            "followers": int,          # フォロワー数
            "following": int,          # フォロー数
            "created_at": str,         # アカウント作成日（ISO 8601）
            "bio": str,                # プロフィールのBio
            "languages": dict,         # 言語統計 {"Python": 5, "JavaScript": 3, ...}
            "total_stars": int,        # 獲得スター数合計
        }

    Raises:
        HTTPException: GitHub API呼び出しが失敗した場合（502 Bad Gateway）

    Security:
        - アクセストークンは判定結果に含めない（メモリ内のみで使用）
        - 外部APIエラーは上位層でキャッチし、ログインフローを継続する
    """
    async with httpx.AsyncClient(timeout=15.0) as client:
        # 1. ユーザー基本情報取得
        try:
            user_resp = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
            user_resp.raise_for_status()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch GitHub user info: {e}")
            raise HTTPException(
                status_code=502,
                detail=f"GitHub APIからユーザー情報を取得できませんでした: {e}",
            ) from e

        user_data = user_resp.json()

        # 2. リポジトリ一覧取得（言語統計とスター数集計用）
        try:
            repos_resp = await client.get(
                f"https://api.github.com/users/{user_data['login']}/repos",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
                params={
                    "per_page": 100,  # 最大100件（GitHub API制限）
                    "sort": "updated",  # 更新日順
                },
            )
            repos_resp.raise_for_status()
        except httpx.HTTPError as e:
            logger.warning(f"Failed to fetch repositories: {e}")
            # リポジトリ取得失敗でもユーザー情報は返却（判定精度は下がるが継続）
            repos = []
        else:
            repos = repos_resp.json()

        # 3. 言語統計を集計
        languages: dict[str, int] = {}
        for repo in repos:
            language = repo.get("language")
            if language:
                languages[language] = languages.get(language, 0) + 1

        # 4. 獲得スター数合計を計算
        total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)

        return {
            "username": user_data["login"],
            "public_repos": user_data.get("public_repos", 0),
            "followers": user_data.get("followers", 0),
            "following": user_data.get("following", 0),
            "created_at": user_data.get("created_at", ""),
            "bio": user_data.get("bio", ""),
            "languages": languages,
            "total_stars": total_stars,
        }
