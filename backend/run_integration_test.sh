#!/bin/bash
#
# AIランク分析のクイックテスト実行スクリプト
#
# 使い方:
#   ./run_integration_test.sh
#

set -e

cd "$(dirname "$0")"

echo "=========================================="
echo "AI ランク分析 インテグレーションテスト"
echo "=========================================="
echo ""

# APIキーの確認
if [ ! -f .env ]; then
    echo "❌ Error: .env ファイルが見つかりません"
    echo ""
    echo "以下のコマンドで .env ファイルを作成してください:"
    echo "  cp .env.example .env"
    echo ""
    echo "その後、.env ファイルを編集して実際のAPIキーを設定してください。"
    exit 1
fi

# APIキーが設定されているか確認
if grep -q "REPLACE_WITH_YOUR" .env; then
    echo "⚠️  Warning: .env ファイルにダミーのAPIキーが含まれています"
    echo ""
    echo ".env ファイルを編集して、実際のAPIキーを設定してください:"
    echo "  - OPENAI_API_KEY (OpenAIを使用する場合)"
    echo "  - ANTHROPIC_API_KEY (Anthropicを使用する場合)"
    echo ""
    read -p "このまま続行しますか？ (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ 環境設定を確認しました"
echo ""

# 依存関係のインストール確認
echo "📦 依存関係を確認中..."
if ! poetry --version > /dev/null 2>&1; then
    echo "❌ Error: Poetry がインストールされていません"
    echo "Poetry をインストールしてください: https://python-poetry.org/docs/#installation"
    exit 1
fi

echo "依存関係をインストール中（容量節約のため段階的にインストール）..."
# まずmain依存のみインストール
poetry install --no-interaction --only main --no-root 2>&1 | grep -v "Installing" | head -20 || true

# 次にtest依存（pytest等）をインストール（ruffはスキップ）
poetry install --no-interaction --with dev --no-root 2>&1 | grep -E "(Installing pytest|Installing fastapi|Error|Failed)" | head -20 || {
    echo "⚠️  一部の依存関係のインストールに失敗しましたが続行します"
}
echo ""

# テストの選択肢を表示
echo "実行するテストを選択してください:"
echo "  1) サービス層テスト (test_rank_service_integration.py)"
echo "  2) API層テスト (test_analyze_integration.py)"
echo "  3) 全てのインテグレーションテスト"
echo "  4) カスタムテスト（自分の情報でテスト）"
echo ""
read -p "選択 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🚀 サービス層テストを実行中..."
        poetry run pytest tests/test_services/test_rank_service_integration.py -v -s
        ;;
    2)
        echo ""
        echo "🚀 API層テストを実行中..."
        poetry run pytest tests/test_api/test_analyze_integration.py -v -s
        ;;
    3)
        echo ""
        echo "🚀 全てのインテグレーションテストを実行中..."
        poetry run pytest -m integration -v -s
        ;;
    4)
        echo ""
        echo "📝 カスタムテストを実行します"
        echo ""
        echo "以下のファイルを編集して、自分の情報を入力してください:"
        echo "  - tests/test_services/test_rank_service_integration.py::test_analyze_custom_user"
        echo "  - tests/test_api/test_analyze_integration.py::test_analyze_rank_endpoint_custom"
        echo ""
        read -p "編集が完了したら Enter キーを押してください..."
        echo ""
        echo "🚀 カスタムテストを実行中..."
        poetry run pytest tests/test_services/test_rank_service_integration.py::test_analyze_custom_user -v -s
        poetry run pytest tests/test_api/test_analyze_integration.py::test_analyze_rank_endpoint_custom -v -s
        ;;
    *)
        echo "❌ 無効な選択です"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "✅ テスト完了"
echo "=========================================="
