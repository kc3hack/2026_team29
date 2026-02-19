#!/bin/bash
#
# AIランク分析のクイックテスト実行スクリプト（容量節約版）
#
# ディスク容量が少ない環境でも実行できるように最適化
#

set -e

cd "$(dirname "$0")"

echo "=========================================="
echo "AI ランク分析 インテグレーションテスト"
echo "（容量節約版）"
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

# 仮想環境の存在確認
if ! poetry env info &>/dev/null || [ "$(poetry env info -p 2>/dev/null)" = "NA" ]; then
    echo "⚠️  Poetry仮想環境が見つかりません"
    echo ""
    echo "容量を節約するために、必要最小限のパッケージのみインストールします..."
    echo ""
    
    # 容量確認
    FREE_SPACE=$(df -h / | tail -1 | awk '{print $4}' | sed 's/Gi//')
    if (( $(echo "$FREE_SPACE < 5" | bc -l) )); then
        echo "⚠️  ディスク容量が不足しています（空き: ${FREE_SPACE}GB）"
        echo ""
        echo "容量を確保するための推奨手順:"
        echo "  1. brew cleanup --prune=all -s  # Homebrewキャッシュをクリア"
        echo "  2. docker system prune -a       # Dockerキャッシュをクリア（使用している場合）"
        echo "  3. ~/Library/Caches を確認して不要なキャッシュを削除"
        echo ""
        read -p "容量不足を無視して続行しますか？ (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # ruffを除いてインストール
    echo "ruffを除外してインストールを試みます..."
    if ! poetry install --no-interaction --no-root 2>&1 | tee /tmp/poetry_install.log; then
        echo ""
        echo "⚠️  完全なインストールに失敗しました"
        echo "エラーログは /tmp/poetry_install.log を確認してください"
        echo ""
        echo "代替案: 必要なパッケージのみpipで直接インストール"
        read -p "pipで必要なパッケージのみインストールしますか？ (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python3 -m pip install --user pytest pytest-asyncio fastapi langchain langchain-openai langchain-anthropic httpx pydantic-settings
            export PYTHONPATH="$PWD:$PYTHONPATH"
            echo "✅ 必要なパッケージをインストールしました"
        else
            exit 1
        fi
    fi
else
    echo "✅ Poetry仮想環境が見つかりました"
    # 念のため必要なパッケージの存在を確認
    if ! poetry run python -c "import pytest; import fastapi; import langchain" 2>/dev/null; then
        echo "⚠️  必要なパッケージが不足しています。インストールを試みます..."
        poetry install --no-interaction --no-root 2>&1 | grep -E "(Installing|Error)" | head -20 || true
    fi
fi

echo ""

# テストの選択肢を表示
echo "実行するテストを選択してください:"
echo "  1) サービス層テスト (test_rank_service_integration.py)"
echo "  2) API層テスト (test_analyze_integration.py)"
echo "  3) 全てのインテグレーションテスト"
echo "  4) 単一テスト（高速・推奨）"
echo ""
read -p "選択 (1-4): " choice

# Poetryが使える場合はpoetry run、そうでない場合はpython3直接実行
if poetry env info &>/dev/null && [ "$(poetry env info -p 2>/dev/null)" != "NA" ]; then
    TEST_CMD="poetry run pytest"
else
    TEST_CMD="python3 -m pytest"
    export PYTHONPATH="$PWD:$PYTHONPATH"
fi

case $choice in
    1)
        echo ""
        echo "🚀 サービス層テストを実行中..."
        $TEST_CMD tests/test_services/test_rank_service_integration.py -v -s
        ;;
    2)
        echo ""
        echo "🚀 API層テストを実行中..."
        $TEST_CMD tests/test_api/test_analyze_integration.py -v -s
        ;;
    3)
        echo ""
        echo "🚀 全てのインテグレーションテストを実行中..."
        $TEST_CMD -m integration -v -s
        ;;
    4)
        echo ""
        echo "🚀 単一テストを実行します（最も高速）"
        echo ""
        echo "基本的なランク分析テストを実行中..."
        $TEST_CMD tests/test_services/test_rank_service_integration.py::test_analyze_real_user_rank -v -s
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
