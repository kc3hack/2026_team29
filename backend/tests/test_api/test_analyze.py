"""
ランク判定APIエンドポイントのテスト

FastAPIのテストクライアントを使用
"""

import json
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_analyze_rank_success():
    """正常系: POST /api/v1/analyze/rank"""
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

        response = client.post(
            "/api/v1/analyze/rank",
            json={
                "github_username": "octocat",
                "portfolio_text": "個人サイト: https://example.com",
                "qiita_id": "example_user",
                "other_info": "LeetCode参加者",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["rank"] == 4
        assert data["rank_name"] == "母樹"
        assert data["percentile"] == 65.0


def test_analyze_rank_minimal():
    """GitHub username のみでのリクエスト"""
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

        response = client.post(
            "/api/v1/analyze/rank",
            json={"github_username": "test_user"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["rank"] == 2
        assert data["rank_name"] == "若木"


def test_analyze_rank_invalid_username():
    """エラー系: 空のgithub_usernameは不許可"""
    response = client.post(
        "/api/v1/analyze/rank",
        json={"github_username": ""},
    )

    assert response.status_code == 422  # Validation error
