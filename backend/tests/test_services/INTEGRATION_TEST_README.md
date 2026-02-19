# ランク分析AI インテグレーションテスト実行手順

実際のLLM APIを使用してランク分析機能をテストします。

## 前提条件

OpenAIまたはAnthropicのAPIキーが必要です。

## 手順

### 1. APIキーの設定

`backend/.env` ファイルを編集して、実際のAPIキーを設定してください。

```bash
cd backend
cp .env.example .env  # まだ.envファイルがない場合
```

`.env` ファイルを編集：

```dotenv
# OpenAIを使う場合
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
OPENAI_MODEL=gpt-4o-mini

# Anthropicを使う場合（代替）
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-your-actual-api-key-here
# ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

### 2. 依存関係のインストール

```bash
cd backend
poetry install
```

### 3. テストの実行

#### 全インテグレーションテストを実行（サービス層 + API層）

```bash
# サービス層のテスト
poetry run pytest tests/test_services/test_rank_service_integration.py -v -s

# API層のテスト
poetry run pytest tests/test_api/test_analyze_integration.py -v -s

# 全てのインテグレーションテストを実行
poetry run pytest -m integration -v -s
```

オプション：

- `-v`: 詳細な出力
- `-s`: print文の出力を表示（AIの判定結果が見られます）

#### 特定のテストのみ実行

```bash
# 基本テスト
poetry run pytest tests/test_services/test_rank_service_integration.py::test_analyze_real_user_rank -v -s

# 初心者レベルのテスト
poetry run pytest tests/test_services/test_rank_service_integration.py::test_analyze_beginner_user -v -s

# 中級者レベルのテスト
poetry run pytest tests/test_services/test_rank_service_integration.py::test_analyze_intermediate_user -v -s

# 自分でカスタマイズして実行
poetry run pytest tests/test_services/test_rank_service_integration.py::test_analyze_custom_user -v -s
```

### 4. カスタムテスト（自分の情報でテスト）

`tests/test_services/test_rank_service_integration.py` の `test_analyze_custom_user` 関数を編集：

```python
result = await analyze_user_rank(
    github_username="your_actual_github_username",
    portfolio_text="あなたのポートフォリオ情報",
    qiita_id="your_qiita_id",
    other_info="その他の活動",
)
```

実行：

```bash
poetry run pytest tests/test_services/test_rank_service_integration.py::test_analyze_custom_user -v -s
```

## 出力例

テストが成功すると、以下のような出力が表示されます：

```
=== LLM Response ===
{
  "percentile": 99.95,
  "rank": 9,
  "rank_name": "世界樹",
  "reasoning": "Linux kernelの開発者であり、Gitの発明者として世界中のエンジニアに影響を与えています。技術の幅、深さ、継続性、コミュニティへの貢献のすべてにおいて最高レベルです。プレデター級、上位0.05%に位置します。"
}
========================================
```

## トラブルシューティング

### APIキーエラー

```
OPENAI_API_KEY not set. Please set it in .env file.
```

→ `.env` ファイルに正しいAPIキーが設定されているか確認してください。

### タイムアウトエラー

```
Timeout waiting for response
```

→ ネットワーク接続を確認するか、`backend/app/core/llm.py` の `timeout` パラメータを増やしてください。

### API料金の確認

- OpenAI: https://platform.openai.com/usage
- Anthropic: https://console.anthropic.com/settings/usage

gpt-4o-mini は非常に安価なので、テスト実行で数円程度です。

## 通常のユニットテスト（モック使用）

APIキーを使わない通常のテストは以下で実行できます：

```bash
poetry run pytest tests/test_services/test_rank_service.py -v
```

こちらはモックを使用しているため、APIキーは不要です。
