"""
ランク判定サービスのテスト

LLM呼び出しをモック化してテスト
"""

import json
import pytest
from unittest.mock import AsyncMock, patch
from app.services.rank_service import analyze_user_rank


@pytest.mark.asyncio
async def test_analyze_user_rank_success():
    """正常系: LLMから正しいJSON応答を取得"""
    mock_response = {
        "percentile": 65.0,
        "rank": 4,
        "rank_name": "母樹",
        "reasoning": "複数の技術での実装経験が確認されました。",
    }

    with patch("app.services.rank_service.invoke_llm", new_callable=AsyncMock) as mock_invoke:
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
    with patch("app.services.rank_service.invoke_llm", new_callable=AsyncMock) as mock_invoke:
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

    with patch("app.services.rank_service.invoke_llm", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = json.dumps(mock_response)

        result = await analyze_user_rank(github_username="test_user")

        assert result["rank"] == 2
        assert result["rank_name"] == "若木"
