"""
ランク判定APIエンドポイントのインテグレーションテスト

実際のLLM APIを使用してFastAPIエンドポイントをテスト。
環境変数に有効なAPIキーが必要。

実行方法:
    pytest tests/test_api/test_analyze_integration.py -v -s
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


client = TestClient(app)


@pytest.mark.integration
def test_analyze_rank_endpoint_real_api():
    """
    実際のLLM APIを使用したエンドポイントテスト

    検証項目:
    - POST /api/v1/analyze/rank が正常に動作する
    - レスポンスが正しいスキーマに従っている
    - ステータスコード 200 が返る
    """
    # APIキーが設定されているか確認
    if settings.LLM_PROVIDER.lower() == "openai":
        if not settings.OPENAI_API_KEY or "REPLACE" in settings.OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set. Please set it in .env file.")
    elif settings.LLM_PROVIDER.lower() == "anthropic":
        if not settings.ANTHROPIC_API_KEY or "REPLACE" in settings.ANTHROPIC_API_KEY:
            pytest.skip("ANTHROPIC_API_KEY not set. Please set it in .env file.")

    # テストリクエスト
    response = client.post(
        "/api/v1/analyze/rank",
        json={
            "github_username": "torvalds",
            "portfolio_text": "Linux kernel creator, Git inventor",
            "qiita_id": "",
            "other_info": "Created Linux operating system and Git version control",
        },
    )

    # レスポンス検証
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()

    # スキーマ検証
    assert "percentile" in data, "percentile field is missing"
    assert "rank" in data, "rank field is missing"
    assert "rank_name" in data, "rank_name field is missing"
    assert "reasoning" in data, "reasoning field is missing"

    # 値の範囲検証
    assert (
        0.0 <= data["percentile"] <= 100.0
    ), f"percentile out of range: {data['percentile']}"
    assert 0 <= data["rank"] <= 9, f"rank out of range: {data['rank']} (expected 0-9)"
    assert isinstance(data["rank_name"], str), "rank_name must be string"
    assert len(data["reasoning"]) > 0, "reasoning must not be empty"

    # デバッグ出力
    print("\n=== API Response ===")
    print(f"Status Code: {response.status_code}")
    print(f"Percentile: {data['percentile']}")
    print(f"Rank: {data['rank']} ({data['rank_name']})")
    print(f"Reasoning: {data['reasoning']}")
    print("=" * 40)


@pytest.mark.integration
def test_analyze_rank_endpoint_beginner():
    """
    初心者レベルのリクエストでテスト
    """
    if settings.LLM_PROVIDER.lower() == "openai":
        if not settings.OPENAI_API_KEY or "REPLACE" in settings.OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set")
    elif settings.LLM_PROVIDER.lower() == "anthropic":
        if not settings.ANTHROPIC_API_KEY or "REPLACE" in settings.ANTHROPIC_API_KEY:
            pytest.skip("ANTHROPIC_API_KEY not set")

    response = client.post(
        "/api/v1/analyze/rank",
        json={
            "github_username": "newuser123",
            "portfolio_text": "プログラミング学習中",
            "qiita_id": "",
            "other_info": "Progateで HTML/CSS を学習",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "percentile" in data
    assert "rank" in data
    assert "rank_name" in data
    assert "reasoning" in data

    print("\n=== Beginner API Response ===")
    print(f"Percentile: {data['percentile']}")
    print(f"Rank: {data['rank']} ({data['rank_name']})")
    print(f"Reasoning: {data['reasoning']}")
    print("=" * 40)


@pytest.mark.integration
def test_analyze_rank_endpoint_minimal_input():
    """
    最小限の入力（GitHub username のみ）でテスト
    """
    if settings.LLM_PROVIDER.lower() == "openai":
        if not settings.OPENAI_API_KEY or "REPLACE" in settings.OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set")
    elif settings.LLM_PROVIDER.lower() == "anthropic":
        if not settings.ANTHROPIC_API_KEY or "REPLACE" in settings.ANTHROPIC_API_KEY:
            pytest.skip("ANTHROPIC_API_KEY not set")

    response = client.post(
        "/api/v1/analyze/rank",
        json={"github_username": "test_user"},
    )

    assert response.status_code == 200
    data = response.json()

    assert "percentile" in data
    assert "rank" in data
    assert "rank_name" in data
    assert "reasoning" in data

    print("\n=== Minimal Input API Response ===")
    print(f"Percentile: {data['percentile']}")
    print(f"Rank: {data['rank']} ({data['rank_name']})")
    print(f"Reasoning: {data['reasoning']}")
    print("=" * 40)


@pytest.mark.integration
def test_analyze_rank_endpoint_custom():
    """
    カスタムユーザー情報でテスト（自分の情報でカスタマイズ可能）
    """
    if settings.LLM_PROVIDER.lower() == "openai":
        if not settings.OPENAI_API_KEY or "REPLACE" in settings.OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set")
    elif settings.LLM_PROVIDER.lower() == "anthropic":
        if not settings.ANTHROPIC_API_KEY or "REPLACE" in settings.ANTHROPIC_API_KEY:
            pytest.skip("ANTHROPIC_API_KEY not set")

    # ここをカスタマイズして実行
    response = client.post(
        "/api/v1/analyze/rank",
        json={
            "github_username": "your_github_username",
            "portfolio_text": "あなたのポートフォリオ情報",
            "qiita_id": "your_qiita_id",
            "other_info": "その他の活動",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "percentile" in data
    assert "rank" in data
    assert "rank_name" in data
    assert "reasoning" in data

    print("\n=== Custom User API Response ===")
    print(f"Status Code: {response.status_code}")
    print(f"Percentile: {data['percentile']} (上位 {100 - data['percentile']:.1f}%)")
    print(f"Rank: {data['rank']} ({data['rank_name']})")
    print(f"Reasoning: {data['reasoning']}")
    print("=" * 40)
