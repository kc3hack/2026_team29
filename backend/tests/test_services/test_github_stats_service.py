"""
GitHub統計サービスのテスト (Issue #105)
"""

import httpx
import pytest
from unittest.mock import AsyncMock, Mock, patch

from app.services.github_stats_service import fetch_github_user_stats


@pytest.mark.asyncio
async def test_fetch_github_user_stats_success():
    """GitHub APIから正常に統計情報を取得できること"""
    # モックレスポンスデータ
    mock_user_data = {
        "login": "test_user",
        "id": 12345,
        "public_repos": 42,
        "followers": 100,
        "following": 50,
        "created_at": "2020-01-01T00:00:00Z",
        "bio": "Test engineer",
    }

    mock_repos_data = [
        {
            "name": "repo1",
            "language": "Python",
            "stargazers_count": 10,
        },
        {
            "name": "repo2",
            "language": "JavaScript",
            "stargazers_count": 5,
        },
        {
            "name": "repo3",
            "language": "Python",
            "stargazers_count": 3,
        },
        {
            "name": "repo4",
            "language": None,  # 言語なしのリポジトリ
            "stargazers_count": 0,
        },
    ]

    # httpx.AsyncClient.get をモック
    mock_responses = [
        # 1回目: ユーザー情報取得
        Mock(json=lambda: mock_user_data, raise_for_status=lambda: None),
        # 2回目: リポジトリ一覧取得
        Mock(json=lambda: mock_repos_data, raise_for_status=lambda: None),
    ]

    async def mock_get(*args, **kwargs):
        return mock_responses.pop(0)

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=mock_get)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "app.services.github_stats_service.httpx.AsyncClient",
        return_value=mock_client,
    ):
        # テスト実行
        result = await fetch_github_user_stats("test_access_token")

        # アサーション
        assert result["username"] == "test_user"
        assert result["public_repos"] == 42
        assert result["followers"] == 100
        assert result["following"] == 50
        assert result["created_at"] == "2020-01-01T00:00:00Z"
        assert result["bio"] == "Test engineer"
        assert result["languages"] == {"Python": 2, "JavaScript": 1}
        assert result["total_stars"] == 18  # 10 + 5 + 3 + 0


@pytest.mark.asyncio
async def test_fetch_github_user_stats_user_api_error():
    """GitHub API（ユーザー情報取得）呼び出し失敗時にHTTPExceptionが発生すること"""
    # httpx.AsyncClient.get をモック（エラー発生）
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=httpx.HTTPError("API Error"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "app.services.github_stats_service.httpx.AsyncClient",
        return_value=mock_client,
    ):
        # テスト実行（HTTPExceptionが発生することを期待）
        with pytest.raises(Exception):  # HTTPException or httpx.HTTPError
            await fetch_github_user_stats("test_access_token")


@pytest.mark.asyncio
async def test_fetch_github_user_stats_repos_api_error():
    """リポジトリ取得失敗時でもユーザー情報は返却されること"""
    # モックレスポンスデータ
    mock_user_data = {
        "login": "test_user",
        "id": 12345,
        "public_repos": 10,
        "followers": 50,
        "following": 30,
        "created_at": "2021-01-01T00:00:00Z",
        "bio": "Developer",
    }

    # httpx.AsyncClient.get をモック
    mock_responses = [
        # 1回目: ユーザー情報取得（成功）
        Mock(json=lambda: mock_user_data, raise_for_status=lambda: None),
        # 2回目: リポジトリ一覧取得（失敗）
        Mock(side_effect=httpx.HTTPError("Repos API Error")),
    ]

    async def mock_get(*args, **kwargs):
        response = mock_responses.pop(0)
        if isinstance(response, Mock) and response.side_effect:
            raise response.side_effect
        return response

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=mock_get)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "app.services.github_stats_service.httpx.AsyncClient",
        return_value=mock_client,
    ):
        # テスト実行
        result = await fetch_github_user_stats("test_access_token")

        # アサーション（ユーザー情報は取得できている）
        assert result["username"] == "test_user"
        assert result["public_repos"] == 10
        assert result["followers"] == 50
        # リポジトリ情報は取得できていないため空
        assert result["languages"] == {}
        assert result["total_stars"] == 0


@pytest.mark.asyncio
async def test_fetch_github_user_stats_empty_repos():
    """リポジトリが0件の場合でも正常に処理されること"""
    # モックレスポンスデータ
    mock_user_data = {
        "login": "new_user",
        "id": 99999,
        "public_repos": 0,
        "followers": 0,
        "following": 0,
        "created_at": "2025-01-01T00:00:00Z",
        "bio": "",
    }

    # httpx.AsyncClient.get をモック
    mock_responses = [
        # 1回目: ユーザー情報取得
        Mock(json=lambda: mock_user_data, raise_for_status=lambda: None),
        # 2回目: リポジトリ一覧取得（空配列）
        Mock(json=lambda: [], raise_for_status=lambda: None),
    ]

    async def mock_get(*args, **kwargs):
        return mock_responses.pop(0)

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=mock_get)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "app.services.github_stats_service.httpx.AsyncClient",
        return_value=mock_client,
    ):
        # テスト実行
        result = await fetch_github_user_stats("test_access_token")

        # アサーション
        assert result["username"] == "new_user"
        assert result["public_repos"] == 0
        assert result["followers"] == 0
        assert result["languages"] == {}
        assert result["total_stars"] == 0
