"""
LLM基盤のテスト

モックを使用した基本的な動作確認。
実際のAPI呼び出しは手動テストで確認。
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.llm import get_llm, invoke_llm, invoke_llm_sync
from app.core.prompts import build_test_prompt


class TestGetLLM:
    """get_llm関数のテスト"""

    @patch("app.core.llm.settings")
    def test_get_llm_openai(self, mock_settings):
        """OpenAI LLMの初期化テスト"""
        mock_settings.LLM_PROVIDER = "openai"
        mock_settings.OPENAI_MODEL = "gpt-4o-mini"
        mock_settings.OPENAI_API_KEY = "sk-test-key"

        llm = get_llm()
        assert llm is not None
        assert llm.model_name == "gpt-4o-mini"

    @patch("app.core.llm.settings")
    def test_get_llm_anthropic(self, mock_settings):
        """Anthropic LLMの初期化テスト"""
        mock_settings.LLM_PROVIDER = "anthropic"
        mock_settings.ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"
        mock_settings.ANTHROPIC_API_KEY = "anthropic-test-key"

        llm = get_llm()
        assert llm is not None
        assert llm.model == "claude-3-5-sonnet-20241022"

    @patch("app.core.llm.settings")
    def test_get_llm_unsupported_provider(self, mock_settings):
        """未サポートプロバイダーでエラー"""
        mock_settings.LLM_PROVIDER = "unsupported"

        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            get_llm()

    @patch("app.core.llm.settings")
    def test_get_llm_openai_without_api_key(self, mock_settings):
        """OpenAI APIキー未設定時はエラー"""
        mock_settings.LLM_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = ""

        with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
            get_llm()

    @patch("app.core.llm.settings")
    def test_get_llm_anthropic_without_api_key(self, mock_settings):
        """Anthropic APIキー未設定時はエラー"""
        mock_settings.LLM_PROVIDER = "anthropic"
        mock_settings.ANTHROPIC_API_KEY = ""

        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY is required"):
            get_llm()


class TestInvokeLLM:
    """invoke_llm関数のテスト"""

    @pytest.mark.asyncio
    @patch("app.core.llm.get_llm")
    async def test_invoke_llm_success(self, mock_get_llm):
        """正常なLLM呼び出し"""
        # モックレスポンス
        mock_response = MagicMock()
        mock_response.content = "Hello, world!"

        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        result = await invoke_llm("Test prompt")

        assert result == "Hello, world!"
        mock_llm.ainvoke.assert_called_once_with("Test prompt")

    @pytest.mark.asyncio
    @patch("app.core.llm.get_llm")
    async def test_invoke_llm_error(self, mock_get_llm):
        """LLM呼び出しエラー時の挙動"""
        mock_llm = AsyncMock()
        mock_llm.ainvoke.side_effect = Exception("API Error")
        mock_get_llm.return_value = mock_llm

        with pytest.raises(Exception, match="API Error"):
            await invoke_llm("Test prompt")


class TestInvokeLLMSync:
    """invoke_llm_sync関数のテスト"""

    @patch("app.core.llm.get_llm")
    def test_invoke_llm_sync_success(self, mock_get_llm):
        """同期LLM呼び出し"""
        mock_response = MagicMock()
        mock_response.content = "Sync response"

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        result = invoke_llm_sync("Test prompt")

        assert result == "Sync response"
        mock_llm.invoke.assert_called_once_with("Test prompt")


class TestPrompts:
    """プロンプトヘルパーのテスト"""

    def test_build_test_prompt(self):
        """テストプロンプト生成"""
        prompt = build_test_prompt("こんにちは")
        assert "こんにちは" in prompt
        assert "応答してください" in prompt
