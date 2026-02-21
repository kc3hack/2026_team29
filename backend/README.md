# Backend API

FastAPI + SQLAlchemy + PostgreSQL（開発時はSQLite）

## セットアップ

### 1. 環境変数の設定

```bash
cd backend
cp .env.example .env
# .envファイルを編集して必要なAPIキーを設定
```

### 2. マイグレーション実行

```bash
poetry install
poetry run alembic upgrade head
```

### 3. テストデータの投入

スキルツリー生成APIなど、ユーザーデータが必要なエンドポイントをテストするには、まずテストユーザーを作成する必要があります。

```bash
poetry run python scripts/seed_test_data.py
```

実行すると以下の3ユーザーが作成されます:

- **test_beginner** (rank=2, github_username=beginner123)
- **test_intermediate** (rank=5, github_username=Inlet-back)
- **test_advanced** (rank=8, github_username=torvalds)

### 4. サーバー起動

```bash
# 開発サーバー（ホットリロード有効）
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

または Docker Compose を使用:

```bash
cd ..  # プロジェクトルートに戻る
docker-compose up -d backend
```

## API動作確認

### ヘルスチェック

```bash
curl http://localhost:8000/health
```

### 認証フロー (Issue #59, ADR 014)

> **必須環境変数** (未設定の場合起動時エラーまたは 503):
>
> | 変数名 | 用途 | 生成方法 |
> |------------|------|----------|
> | `ENCRYPTION_KEY` | OAuth トークンの暗号化 | `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
> | `JWT_SECRET_KEY` | JWT 署名・検証 | `python -c "import secrets; print(secrets.token_hex(32))"` |
> | `FRONTEND_URL` | OAuth リダイレクト先 | `http://localhost:3000`（デフォルト） |
> | `GITHUB_CLIENT_ID` | GitHub OAuth（任意） | GitHub アプリ設定画面で取得 |
> | `GITHUB_CLIENT_SECRET` | GitHub OAuth（任意） | 同上 |
>
> `ENCRYPTION_KEY` と `JWT_SECRET_KEY` は **起動時にプロセスを即座停止**する。`.env.example` をコピーして必ず設定すること。

```bash
# 1. ブラウザで GitHub ログイン開始
open http://localhost:8000/api/v1/auth/github/login
# → GitHub 認可ページへリダイレクト
# → 認可後 /api/v1/auth/github/callback が呼ばれる
# → JWT が httpOnly Cookie にセットされ http://localhost:3000 へリダイレクト

# 2. 認証確認（Cookie を保存しつつ送信）
curl -b cookies.txt -c cookies.txt http://localhost:8000/api/v1/users/me | jq

# 3. ログアウト（POST に変更、保存した Cookie を送信）
curl -b cookies.txt -c cookies.txt -X POST http://localhost:8000/api/v1/auth/logout
```

**テスト・API クライアントから呼ぶ場合（Bearer トークン）:**
```bash
# JWT を直接取得する方法（テスト用: conftest.py の fixture を参照）
curl -H "Authorization: Bearer <jwt>" http://localhost:8000/api/v1/users/me | jq
```

> **Note**: フロントエンドから fetch する場合は `credentials: 'include'` が必要。
> Cookie を使うため `BACKEND_CORS_ORIGINS` に `FRONTEND_URL` を含めること。

### ユーザー情報取得 (ADR 015)

```bash
# 自分の情報
curl -b cookies.txt http://localhost:8000/api/v1/users/me | jq

# 自分のスキルツリー
curl -b cookies.txt http://localhost:8000/api/v1/users/me/skill-trees | jq

# 自分のクエスト進捗
curl -b cookies.txt http://localhost:8000/api/v1/users/me/quest-progress | jq
```

### スキルツリー生成 (Issue #54)

```bash
# テストユーザー（user_id=1）でスキルツリー生成
curl -X POST http://localhost:8000/api/v1/analyze/skill-tree \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "category": "web"
  }' | jq

# クリア済みスキルのみ表示
curl -X POST http://localhost:8000/api/v1/analyze/skill-tree \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "category": "web"
  }' | jq '.tree_data.nodes[] | select(.completed == true) | {id, name, completed}'
```

**カテゴリ一覧**:

- `web`: Web開発
- `ai`: AI/機械学習
- `security`: セキュリティ
- `infrastructure`: インフラ/DevOps
- `design`: UI/UXデザイン
- `game`: ゲーム開発

### ランク判定 (Issue #36)

```bash
curl -X POST http://localhost:8000/api/v1/analyze/rank \
  -H "Content-Type: application/json" \
  -d '{
    "github_username": "torvalds",
    "portfolio_text": "Linux kernel creator",
    "qiita_id": "",
    "other_info": "Created Linux and Git"
  }' | jq
```

## テスト実行

### 全テスト実行

```bash
poetry run pytest -v
```

### 特定のテストファイル実行

```bash
# スキルツリーサービスのテスト
poetry run pytest tests/test_services/test_skill_tree_service.py -v

# APIエンドポイントのテスト
poetry run pytest tests/test_api/test_analyze_mock.py -v
```

### 統合テスト（実際のLLM API使用）

```bash
# .envにAPIキーが必要
poetry run pytest tests/test_api/test_analyze_integration.py -v -s
```

## 開発ガイド

### コードスタイル

```bash
# Ruffでリント・フォーマット
poetry run ruff check .
poetry run ruff format .
```

### 新しいマイグレーション作成

```bash
poetry run alembic revision --autogenerate -m "説明"
poetry run alembic upgrade head
```

### デバッグ

モデル定義や依存関係の問題で困ったときは:

1. `app/db/base.py` で全モデルがインポートされているか確認
2. `app/main.py` で `from app.db import base` がインポートされているか確認（SQLAlchemy model registration）

## 主要な実装

- **AI Phase 3 - スキルツリー生成**: `app/services/skill_tree_service.py` (Issue #54)
  - LLM + GitHub API統合
  - 10分間キャッシュ（ハッカソン用最適化）
  - 6カテゴリ対応（web/ai/security/infrastructure/design/game）
- **AI Phase 2 - ランク判定**: `app/services/rank_service.py` (Issue #36)
  - LLM活用、GitHub/Qiita連携
- **GitHub API統合**: `app/services/github_service.py` (Issue #54)
  - リポジトリ分析、使用言語抽出、習得済みスキル推定

## API仕様

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 管理API: http://localhost:8000/admin/docs (X-Admin-Key ヘッダー認証必須)
