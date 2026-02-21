"""
ランク判定サービスのテスト

LLM呼び出しをモック化してテスト
"""

import json
import pytest
from unittest.mock import AsyncMock, Mock, patch
from app.services.rank_service import (
    analyze_user_rank,
    analyze_user_rank_from_github,
    estimate_exp_from_rank,
)


@pytest.mark.asyncio
async def test_analyze_user_rank_success():
    """正常系: LLMから正しいJSON応答を取得"""
    mock_response = {
        "percentile": 65.0,
        "rank": 4,
        "rank_name": "母樹",
        "reasoning": "複数の技術での実装経験が確認されました。",
    }

    with patch(
        "app.services.rank_service.invoke_llm", new_callable=AsyncMock
    ) as mock_invoke:
        mock_invoke.return_value = json.dumps(mock_response)

        result = await analyze_user_rank(
            github_username="octocat",
            portfolio_text="個人サイト: https://example.com",
            qiita_id="example_user",
            other_info="LeetCode参加者",
        )

        assert result == mock_response
        mock_invoke.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_user_rank_fallback():
    """エラー系: JSONパースエラー時はデフォルト値を返す"""
    with patch(
        "app.services.rank_service.invoke_llm", new_callable=AsyncMock
    ) as mock_invoke:
        # 不正なJSON応答
        mock_invoke.return_value = "This is not JSON"

        result = await analyze_user_rank(
            github_username="octocat",
            portfolio_text="",
            qiita_id="",
            other_info="",
        )

        # デフォルト値が返される
        assert result["rank"] == 3
        assert result["rank_name"] == "巨木"
        assert result["percentile"] == 50.0


@pytest.mark.asyncio
async def test_analyze_user_rank_minimal_input():
    """GitHub username のみでテスト"""
    mock_response = {
        "percentile": 30.0,
        "rank": 2,
        "rank_name": "若木",
        "reasoning": "基本スキルは確認されました。",
    }

    with patch(
        "app.services.rank_service.invoke_llm", new_callable=AsyncMock
    ) as mock_invoke:
        mock_invoke.return_value = json.dumps(mock_response)

        result = await analyze_user_rank(github_username="test_user")

        assert result["rank"] == 2
        assert result["rank_name"] == "若木"


# ============================================================
# GitHub OAuth用ランク判定のテスト (Issue #105)
# ============================================================


@pytest.mark.asyncio
async def test_analyze_user_rank_from_github_success():
    """GitHub統計情報から正常にランク判定ができること"""
    github_stats = {
        "username": "octocat",
        "public_repos": 50,
        "followers": 100,
        "following": 50,
        "created_at": "2015-01-01T00:00:00Z",
        "bio": "Senior Software Engineer",
        "languages": {"Python": 20, "JavaScript": 15, "Go": 10},
        "total_stars": 500,
    }

    mock_llm_response = {
        "percentile": 85.0,
        "rank": 5,
        "rank_name": "林",
        "reasoning": "長期間の活動実績と多様な技術スタックが確認されました。",
    }

    with patch(
        "app.services.rank_service.invoke_llm", new_callable=AsyncMock
    ) as mock_invoke:
        mock_invoke.return_value = json.dumps(mock_llm_response)

        result = await analyze_user_rank_from_github(
            github_stats=github_stats, profile=None
        )

        # LLMの応答に加えて、estimated_expが計算されていること
        assert result["rank"] == 5
        assert result["rank_name"] == "林"
        assert result["percentile"] == 85.0
        assert "estimated_exp" in result
        assert result["estimated_exp"] > 0


@pytest.mark.asyncio
async def test_analyze_user_rank_from_github_with_profile():
    """プロフィール情報を含めた判定が可能であること"""
    github_stats = {
        "username": "test_user",
        "public_repos": 10,
        "followers": 5,
        "following": 10,
        "created_at": "2023-01-01T00:00:00Z",
        "bio": "",
        "languages": {"Python": 5},
        "total_stars": 10,
    }

    # モックProfile
    mock_profile = Mock()
    mock_profile.portfolio_text = "個人サイト: https://example.com"
    mock_profile.qiita_id = "test_qiita"
    mock_profile.connpass_id = "test_user"
    mock_profile.portfolio_url = "https://portfolio.example.com"

    mock_llm_response = {
        "percentile": 60.0,
        "rank": 3,
        "rank_name": "巨木",
        "reasoning": "GitHub実績は少ないが、追加情報から学習意欲が確認されました。",
    }

    with patch(
        "app.services.rank_service.invoke_llm", new_callable=AsyncMock
    ) as mock_invoke:
        mock_invoke.return_value = json.dumps(mock_llm_response)

        result = await analyze_user_rank_from_github(
            github_stats=github_stats, profile=mock_profile
        )

        assert result["rank"] == 3
        assert result["rank_name"] == "巨木"
        assert "estimated_exp" in result


@pytest.mark.asyncio
async def test_analyze_user_rank_from_github_fallback():
    """LLM呼び出し失敗時にデフォルト値が返されること"""
    github_stats = {
        "username": "test_user",
        "public_repos": 5,
        "followers": 1,
        "following": 2,
        "created_at": "2024-01-01T00:00:00Z",
        "bio": "",
        "languages": {},
        "total_stars": 0,
    }

    with patch(
        "app.services.rank_service.invoke_llm", new_callable=AsyncMock
    ) as mock_invoke:
        # 不正なJSON応答
        mock_invoke.return_value = "Invalid JSON response"

        result = await analyze_user_rank_from_github(
            github_stats=github_stats, profile=None
        )

        # デフォルト值が返される
        assert result["rank"] == 3
        assert result["rank_name"] == "巨木"
        assert result["percentile"] == 50.0
        assert result["estimated_exp"] == 800  # estimate_exp_from_rank(3) = (600+1000)//2


def test_estimate_exp_from_rank():
    """ランクから経験値を正しく推定できること"""
    # rank 0 (種子): 0 ~ 100 の中央値
    assert estimate_exp_from_rank(0) == 50

    # rank 3 (巨木): 600 ~ 1000 の中央値
    assert estimate_exp_from_rank(3) == 800

    # rank 5 (林): 1500 ~ 2500 の中央値
    assert estimate_exp_from_rank(5) == 2000

    # rank 9 (世界樹): 最高ランク（9000 + 500）
    assert estimate_exp_from_rank(9) == 9500

    # 範囲外のランク（通常発生しないがフォールバック）
    assert estimate_exp_from_rank(99) > 9000
