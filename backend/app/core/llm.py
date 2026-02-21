"""
LLM統合モジュール

LangChainを使用したOpenAI/Anthropic API呼び出しの基盤。
環境変数でプロバイダーを切り替え可能。
"""

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from app.core.config import settings


def get_llm(
    model: str | None = None,
    temperature: float = 0.7,
    timeout: int = 60,
    max_retries: int = 3,
) -> BaseChatModel:
    """
    LLMインスタンスを取得（OpenAI/Anthropic自動切り替え）

    Args:
        model: モデル名（None時は設定から取得）
        temperature: 応答のランダム性（0.0-1.0）
        timeout: タイムアウト時間（秒）
        max_retries: リトライ回数

    Returns:
        BaseChatModel: LangChain ChatModel

    Raises:
        ValueError: 未サポートのLLMプロバイダーまたはAPIキー未設定
    """
    provider = settings.LLM_PROVIDER.lower()

    if provider == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is required when LLM_PROVIDER is 'openai'. "
                "Please set it in your .env file."
            )
        return ChatOpenAI(
            model=model or settings.OPENAI_MODEL,
            temperature=temperature,
            timeout=timeout,
            max_retries=max_retries,
            api_key=settings.OPENAI_API_KEY,
        )
    elif provider == "anthropic":
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY is required when LLM_PROVIDER is 'anthropic'. "
                "Please set it in your .env file."
            )
        return ChatAnthropic(
            model=model or settings.ANTHROPIC_MODEL,
            temperature=temperature,
            timeout=timeout,
            max_retries=max_retries,
            anthropic_api_key=settings.ANTHROPIC_API_KEY,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


async def invoke_llm(
    prompt: str,
    model: str | None = None,
    temperature: float = 0.7,
) -> str:
    """
    LLMに非同期でプロンプトを送信し、応答を取得

    Args:
        prompt: 入力プロンプト
        model: モデル名（Noneの場合はデフォルト）
        temperature: 応答のランダム性

    Returns:
        str: LLMの応答テキスト

    Raises:
        Exception: API呼び出し失敗時
    """
    llm = get_llm(model=model, temperature=temperature)

    try:
        response = await llm.ainvoke(prompt)
        content = response.content
        # LangChainの応答がリストの場合があるため文字列変換
        if isinstance(content, list):
            content = "".join(str(item) for item in content)
        return str(content)
    except Exception as e:
        # ログ出力（本番環境ではロギングライブラリ使用推奨）
        print(f"LLM invocation failed: {e}")
        raise


async def stream_llm(
    prompt: str,
    model: str | None = None,
    temperature: float = 0.7,
):
    """
    LLMに非同期でプロンプトを送信し、応答をストリーミングで取得

    Args:
        prompt: 入力プロンプト
        model: モデル名（Noneの場合はデフォルト）
        temperature: 応答のランダム性

    Yields:
        str: LLMの応答チャンク

    Raises:
        Exception: API呼び出し失敗時

    Example:
        async for chunk in stream_llm(prompt):
            print(chunk, end="", flush=True)
    """
    llm = get_llm(model=model, temperature=temperature)

    try:
        async for chunk in llm.astream(prompt):
            content = chunk.content
            if isinstance(content, list):
                content = "".join(str(item) for item in content)
            if content:
                yield str(content)
    except Exception as e:
        print(f"LLM streaming failed: {e}")
        raise


def invoke_llm_sync(
    prompt: str,
    model: str | None = None,
    temperature: float = 0.7,
) -> str:
    """
    LLMに同期的にプロンプトを送信し、応答を取得

    Args:
        prompt: 入力プロンプト
        model: モデル名（Noneの場合はデフォルト）
        temperature: 応答のランダム性

    Returns:
        str: LLMの応答テキスト

    Raises:
        Exception: API呼び出し失敗時
    """
    llm = get_llm(model=model, temperature=temperature)

    try:
        response = llm.invoke(prompt)
        content = response.content
        # LangChainの応答がリストの場合があるため文字列変換
        if isinstance(content, list):
            content = "".join(str(item) for item in content)
        return str(content)
    except Exception as e:
        print(f"LLM invocation failed: {e}")
        raise
