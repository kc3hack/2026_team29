"""
ハンズオン演習生成APIエンドポイントのテスト

FastAPIのテストクライアントを使用
"""

import json
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_generate_quest_success():
    """正常系: POST /api/v1/quest/generate"""
    mock_response = {
        "title": "Pythonでウェブスクレイピング",
        "difficulty": "intermediate",
        "estimated_time_minutes": 60,
        "learning_objectives": ["Beautiful Soupの使い方"],
        "steps": [
            {
                "step_number": 1,
                "title": "ライブラリインストール",
                "description": "pip install beautifulsoup4",
                "code_example": "pip install beautifulsoup4 requests",
                "checkpoints": ["インストール完了"],
            }
        ],
        "resources": [],
    }

    with patch("app.services.quest_service.invoke_llm", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = json.dumps(mock_response)

        response = client.post(
            "/api/v1/quest/generate",
            json={
                "document_content": "Pythonでウェブスクレイピングを学ぶ...",
                "user_rank": 3,
                "user_skills": "Python基礎",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Pythonでウェブスクレイピング"
        assert data["difficulty"] == "intermediate"


def test_generate_quest_minimal():
    """最小入力のテスト"""
    mock_response = {
        "title": "Docker入門",
        "difficulty": "beginner",
        "estimated_time_minutes": 40,
        "learning_objectives": ["Dockerの基本操作"],
        "steps": [
            {
                "step_number": 1,
                "title": "Dockerインストール",
                "description": "Docker Desktopをインストール",
                "code_example": "",
                "checkpoints": ["バージョン確認"],
            }
        ],
        "resources": ["https://docs.docker.com/"],
    }

    with patch("app.services.quest_service.invoke_llm", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = json.dumps(mock_response)

        response = client.post(
            "/api/v1/quest/generate",
            json={"document_content": "Dockerの基礎を学ぶチュートリアル", "user_rank": 1},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Docker入門"
        assert data["difficulty"] == "beginner"


def test_generate_quest_invalid_rank():
    """エラー系: ランクが範囲外は422エラー"""
    response = client.post(
        "/api/v1/quest/generate", json={"document_content": "Test", "user_rank": 99}
    )

    assert response.status_code == 422


def test_generate_quest_document_too_short():
    """エラー系: ドキュメントが短すぎる場合は422エラー"""
    response = client.post(
        "/api/v1/quest/generate", json={"document_content": "Short", "user_rank": 2}
    )

    assert response.status_code == 422
