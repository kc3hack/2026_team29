"""
ハンズオン演習生成サービスのテスト

LLM呼び出しをモック化してテスト
"""

import json
import pytest
from unittest.mock import AsyncMock, patch
from app.services.quest_service import generate_handson_quest


@pytest.mark.asyncio
async def test_generate_handson_quest_success():
    """正常系: LLMから正しいJSON応答を取得"""
    mock_response = {
        "title": "Reactカウンターアプリ",
        "difficulty": "beginner",
        "estimated_time_minutes": 45,
        "learning_objectives": ["Stateの理解"],
        "steps": [
            {
                "step_number": 1,
                "title": "セットアップ",
                "description": "プロジェクト作成",
                "code_example": "npx create-react-app",
                "checkpoints": ["起動確認"],
            }
        ],
        "resources": ["https://react.dev/"],
    }

    with patch("app.services.quest_service.invoke_llm", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = json.dumps(mock_response)

        result = await generate_handson_quest(
            document_content="Reactの基本", user_rank=2, user_skills="JavaScript"
        )

        assert result["title"] == "Reactカウンターアプリ"
        assert result["difficulty"] == "beginner"
        assert len(result["steps"]) == 1


@pytest.mark.asyncio
async def test_generate_handson_quest_fallback():
    """エラー系: JSONパースエラー時はデフォルト値を返す"""
    with patch("app.services.quest_service.invoke_llm", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = "Invalid JSON"

        result = await generate_handson_quest(document_content="Test document", user_rank=0)

        assert result["title"] == "演習生成エラー"
        assert result["difficulty"] == "beginner"


@pytest.mark.asyncio
async def test_generate_handson_quest_minimal_input():
    """最小入力のテスト"""
    mock_response = {
        "title": "Python基礎演習",
        "difficulty": "beginner",
        "estimated_time_minutes": 30,
        "learning_objectives": ["Python構文の理解"],
        "steps": [
            {
                "step_number": 1,
                "title": "環境構築",
                "description": "Pythonのインストール",
                "code_example": "",
                "checkpoints": ["Python実行確認"],
            }
        ],
        "resources": [],
    }

    with patch("app.services.quest_service.invoke_llm", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = json.dumps(mock_response)

        result = await generate_handson_quest(
            document_content="Pythonの基本文法について", user_rank=1
        )

        assert result["title"] == "Python基礎演習"
        assert result["difficulty"] == "beginner"
