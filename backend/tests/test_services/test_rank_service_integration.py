"""
ランク判定サービスのインテグレーションテスト

実際のLLM APIを使用したテスト。
環境変数に有効なAPIキーが必要。

実行方法:
    # APIキーを設定してから実行
    pytest tests/test_services/test_rank_service_integration.py -v -s

    # または特定のテストのみ
    pytest tests/test_services/test_rank_service_integration.py::test_analyze_real_user_rank -v -s
"""

import json
import pytest
from app.services.rank_service import analyze_user_rank
from app.core.config import settings


@pytest.mark.integration
@pytest.mark.asyncio
async def test_analyze_real_user_rank():
    """
    実際のLLM APIを使用したランク判定テスト（torvalds: 世界的エンジニア）

    検証項目:
    - API呼び出しが成功する
    - JSON形式で正しい応答が返る
    - 必須フィールド（percentile, rank, rank_name, reasoning）が含まれる
    - percentileが0.0-100.0の範囲内（100=最上位、0=最下位）
    - rankが0-9の範囲内
    - torvaldsは高ランク（rank 8-9, percentile 99+）が期待される
    """
    # APIキーが設定されているか確認
    if settings.LLM_PROVIDER.lower() == "openai":
        if not settings.OPENAI_API_KEY or "REPLACE" in settings.OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set. Please set it in .env file.")
    elif settings.LLM_PROVIDER.lower() == "anthropic":
        if not settings.ANTHROPIC_API_KEY or "REPLACE" in settings.ANTHROPIC_API_KEY:
            pytest.skip("ANTHROPIC_API_KEY not set. Please set it in .env file.")

    # テストデータ
    result = await analyze_user_rank(
        github_username="torvalds",
        portfolio_text="Linux kernel creator, Git inventor",
        qiita_id="",
        other_info="Created Linux operating system and Git version control",
    )

    # 応答形式の検証
    assert "percentile" in result, "percentile field is missing"
    assert "rank" in result, "rank field is missing"
    assert "rank_name" in result, "rank_name field is missing"
    assert "reasoning" in result, "reasoning field is missing"

    # 値の範囲検証
    assert (
        0.0 <= result["percentile"] <= 100.0
    ), f"percentile out of range: {result['percentile']}"
    assert (
        0 <= result["rank"] <= 9
    ), f"rank out of range: {result['rank']} (expected 0-9)"
    assert isinstance(result["rank_name"], str), "rank_name must be string"
    assert len(result["reasoning"]) > 0, "reasoning must not be empty"

    # デバッグ出力（-s オプションで表示）
    print("\n=== LLM Response ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("=" * 40)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_analyze_beginner_user():
    """
    初心者レベルのユーザーでテスト（Progate学習中）

    期待結果:
    - rank が 0-2（種子、苗木、若木）の範囲
    - percentile が低め（0-80程度、上位20-100%に該当）
    """
    if settings.LLM_PROVIDER.lower() == "openai":
        if not settings.OPENAI_API_KEY or "REPLACE" in settings.OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set")
    elif settings.LLM_PROVIDER.lower() == "anthropic":
        if not settings.ANTHROPIC_API_KEY or "REPLACE" in settings.ANTHROPIC_API_KEY:
            pytest.skip("ANTHROPIC_API_KEY not set")

    result = await analyze_user_rank(
        github_username="newuser123",
        portfolio_text="プログラミング学習中",
        qiita_id="",
        other_info="Progateで HTML/CSS を学習",
    )

    assert "percentile" in result
    assert "rank" in result
    assert "rank_name" in result
    assert "reasoning" in result

    # 初心者レベルの判定が適切か
    print("\n=== Beginner User Analysis ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("=" * 40)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_analyze_intermediate_user():
    """
    中級レベルのユーザーでテスト（実務経験あり、個人開発3つ）

    期待結果:
    - rank が 3-5（巨木、母樹、林）の範囲
    - percentile が中～やや高め（80-95程度、上位5-20%に該当）
    """
    if settings.LLM_PROVIDER.lower() == "openai":
        if not settings.OPENAI_API_KEY or "REPLACE" in settings.OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set")
    elif settings.LLM_PROVIDER.lower() == "anthropic":
        if not settings.ANTHROPIC_API_KEY or "REPLACE" in settings.ANTHROPIC_API_KEY:
            pytest.skip("ANTHROPIC_API_KEY not set")

    result = await analyze_user_rank(
        github_username="intermediate_dev",
        portfolio_text="個人開発でWebアプリを3つリリース。React + Node.js使用。",
        qiita_id="intermediate_qiita",
        other_info="技術記事を月1回投稿、AtCoder緑色",
    )

    assert "percentile" in result
    assert "rank" in result
    assert "rank_name" in result
    assert "reasoning" in result

    print("\n=== Intermediate User Analysis ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("=" * 40)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_analyze_minimal_input():
    """
    最小限の入力でテスト（GitHub username のみ）

    検証項目:
    - 空の入力でもAPIが正常に動作する
    - デフォルト値やエラーハンドリングが正しく機能する
    """
    if settings.LLM_PROVIDER.lower() == "openai":
        if not settings.OPENAI_API_KEY or "REPLACE" in settings.OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set")
    elif settings.LLM_PROVIDER.lower() == "anthropic":
        if not settings.ANTHROPIC_API_KEY or "REPLACE" in settings.ANTHROPIC_API_KEY:
            pytest.skip("ANTHROPIC_API_KEY not set")

    result = await analyze_user_rank(
        github_username="test_user",
        portfolio_text="",
        qiita_id="",
        other_info="",
    )

    assert "percentile" in result
    assert "rank" in result
    assert "rank_name" in result
    assert "reasoning" in result

    print("\n=== Minimal Input Analysis ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("=" * 40)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_analyze_custom_user():
    """
    任意のユーザー情報でテスト（カスタマイズ可能）

    このテストを自分の情報でカスタマイズして実行できます。
    """
    if settings.LLM_PROVIDER.lower() == "openai":
        if not settings.OPENAI_API_KEY or "REPLACE" in settings.OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set")
    elif settings.LLM_PROVIDER.lower() == "anthropic":
        if not settings.ANTHROPIC_API_KEY or "REPLACE" in settings.ANTHROPIC_API_KEY:
            pytest.skip("ANTHROPIC_API_KEY not set")

    # ここをカスタマイズして実行
    result = await analyze_user_rank(
        github_username="your_github_username",
        portfolio_text="あなたのポートフォリオ情報をここに入力",
        qiita_id="your_qiita_id",
        other_info="その他の活動（AtCoder、技術ブログなど）",
    )

    assert "percentile" in result
    assert "rank" in result
    assert "rank_name" in result
    assert "reasoning" in result

    print("\n=== Custom User Analysis ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("=" * 40)
    print(f"Percentile: 上位 {100 - result['percentile']:.1f}%")
    print(f"Rank: {result['rank']} ({result['rank_name']})")
    print(f"理由: {result['reasoning']}")
