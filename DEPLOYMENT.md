# Deployment Guide

このプロジェクトのデプロイ手順書（Vercel + Render構成）

## 🏗️ アーキテクチャ

- **フロントエンド**: Vercel (Next.js)
- **バックエンド**: Render (FastAPI + PostgreSQL)

## 📋 前提条件

1. GitHubリポジトリがpublicまたはVercel/Renderに接続可能
2. OpenAI APIキー
3. GitHub OAuth Appの作成

## 🚀 デプロイ手順

### 1. バックエンドのデプロイ (Render)

#### 1.1 Renderダッシュボード

1. https://dashboard.render.com/ にアクセス
2. "New +" → "Web Service" を選択
3. GitHubリポジトリを接続

#### 1.2 Web Service設定

- **Name**: `team29-backend`
- **Region**: Oregon (Free)
- **Branch**: `main` または `develop`
- **Root Directory**: `backend`
- **Runtime**: Python 3
- **Build Command**: `pip install poetry && poetry install --no-dev`
- **Start Command**: `poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### 1.3 環境変数の設定

Renderダッシュボード → Environment で以下を設定:

```bash
# Database (PostgreSQL推奨)
DATABASE_URL=postgresql://user:password@host/dbname

# CORS設定（フロントエンドURLに更新）
BACKEND_CORS_ORIGINS=["https://your-app.vercel.app"]

# 暗号化キー（以下コマンドで生成）
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=<生成した32バイトbase64文字列>

# Admin API Key（任意の安全な文字列）
ADMIN_API_KEY=<ランダム文字列>

# LLM設定
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini

# JWT設定（以下コマンドで生成）
# openssl rand -hex 32
JWT_SECRET_KEY=<64文字の16進数文字列>
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# GitHub OAuth（次のステップで設定）
GITHUB_CLIENT_ID=<後で設定>
GITHUB_CLIENT_SECRET=<後で設定>

# フロントエンドURL（Vercelデプロイ後に更新）
FRONTEND_URL=https://your-app.vercel.app

# Skill Tree Cache
SKILL_TREE_CACHE_MINUTES=10

# 監視・エラー追跡（オプション）
SENTRY_DSN=  # Sentry使用時のみ設定（https://sentry.io/で取得）
```

#### 1.4 PostgreSQLデータベースの作成

1. Render Dashboard → "New +" → "PostgreSQL"
2. **Name**: `team29-db`
3. **Database**, **User**, **Password**を設定
4. "Create Database"
5. 生成された`DATABASE_URL`をコピーして、Web ServiceのDATABASE_URLに設定

#### 1.5 デプロイ

"Create Web Service"をクリックしてデプロイ開始

デプロイが完了したら、バックエンドのURLをメモ:

```
https://team29-backend.onrender.com
```

### 2. GitHub OAuth Appの作成

1. https://github.com/settings/developers にアクセス
2. "New OAuth App"をクリック
3. 以下を設定:
   - **Application name**: Team29 Skill Tree
   - **Homepage URL**: `https://your-app.vercel.app`
   - **Authorization callback URL**: `https://team29-backend.onrender.com/api/v1/auth/github/callback`
4. "Register application"をクリック
5. **Client ID**と**Client Secret**をコピー
6. RenderのEnvironment変数に設定:
   - `GITHUB_CLIENT_ID`: <コピーしたClient ID>
   - `GITHUB_CLIENT_SECRET`: <コピーしたClient Secret>

### 3. フロントエンドのデプロイ (Vercel)

#### 3.1 Vercelダッシュボード

1. https://vercel.com/new にアクセス
2. GitHubリポジトリを接続

#### 3.2 プロジェクト設定

- **Framework Preset**: Next.js
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Install Command**: `npm install`

#### 3.3 環境変数の設定

"Environment Variables"で以下を設定:

```bash
NEXT_PUBLIC_API_URL=https://team29-backend.onrender.com
```

#### 3.4 デプロイ

"Deploy"をクリック

デプロイが完了したら、フロントエンドのURLをメモ:

```
https://your-app.vercel.app
```

### 4. CORS設定の更新

1. RenderのDashboard → team29-backend → Environment
2. `BACKEND_CORS_ORIGINS`を更新:
   ```
   ["https://your-app.vercel.app"]
   ```
3. `FRONTEND_URL`を更新:
   ```
   https://your-app.vercel.app
   ```
4. "Save Changes" → サービスが自動的に再デプロイされます

### 5. GitHub OAuth Appの更新

1. https://github.com/settings/developers
2. 作成したOAuth Appを選択
3. **Homepage URL**を更新: `https://your-app.vercel.app`
4. **Authorization callback URL**は変更不要（バックエンドのURL）

### 6. データベースマイグレーション

RenderのShellまたはローカルから実行:

```bash
# RenderのShell（Dashboard → Shell）
cd backend
poetry run alembic upgrade head
```

## ✅ 動作確認

1. フロントエンドURL（https://your-app.vercel.app）にアクセス
2. "GitHubでログイン"をクリック
3. GitHub OAuth認証が成功すること
4. ランク判定が実行されること
5. スキルツリーが表示されること
6. AI問題生成が動作すること

## 🔧 トラブルシューティング

### CORSエラー

```
Access to fetch at 'https://team29-backend.onrender.com/api/v1/...' from origin 'https://your-app.vercel.app' has been blocked by CORS policy
```

→ RenderのBACKEND_CORS_ORIGINSにフロントエンドのURLが正しく設定されているか確認

### OAuth認証エラー

```
GitHub OAuth failed: redirect_uri_mismatch
```

→ GitHub OAuth AppのAuthorization callback URLがバックエンドのURLと一致しているか確認

### Database接続エラー

```
sqlalchemy.exc.OperationalError: could not connect to server
```

→ DATABASEURLが正しく設定されているか、PostgreSQLサービスが起動しているか確認

### LLM API エラー

```
Quest generation failed: API key invalid
```

→ OPENAI_API_KEYが正しく設定されているか、クレジットが残っているか確認

## 📊 モニタリング・監視基盤

### 標準ログ確認

- **Render Logs**: Dashboard → Logs
- **Vercel Logs**: Dashboard → Deployments → Logs
- **Render Metrics**: Dashboard → Metrics（CPU/メモリ/リクエスト数）

### 推奨監視ツール（全て無料）

#### 1. OpenAI コスト監視（最優先）

```
https://platform.openai.com/account/limits
```

- **学生ハッカソン推奨設定**:
  - Hard Limit: **$10/月**（絶対上限 - これを超えたらAPI停止）
  - Soft Limit: **$5/月**（警告メール - この時点で使い方を見直す）
  - Email通知設定
- **確認頻度**: 週1回（毎週月曜日推奨）
- **💡 節約のコツ**:
  - スキルツリー生成は1カテゴリにつき1回のみ（キャッシュ活用）
  - 問題生成は1日5回までに制限
  - 不要なAPI呼び出しをログで確認して削減

#### 2. UptimeRobot（死活監視）

```
https://uptimerobot.com/
```

- **無料枠**: 50モニター、5分間隔
- **設定するモニター**:
  - Backend Health: `https://team29-backend.onrender.com/api/v1/health`
  - Frontend: `https://your-app.vercel.app/`
  - Interval: 5分
  - Alert Email: あなたのメールアドレス

#### 3. Sentry（エラー追跡）

```
https://sentry.io/
```

- **無料枠**: 5,000イベント/月
- **統合方法**:

  ```bash
  # backend
  poetry add sentry-sdk
  ```

  ```python
  # backend/app/main.py に追加
  import sentry_sdk

  if settings.SENTRY_DSN:
      sentry_sdk.init(
          dsn=settings.SENTRY_DSN,
          traces_sample_rate=0.1,
          environment="production",
      )
  ```

- **環境変数**: `SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx`

#### 4. Render アラート設定

- Dashboard → Settings → Notifications
- 設定推奨項目:
  - Deploy Failure
  - Service Down
  - High CPU (> 80%)
  - High Memory (> 90%)

### 監視チェックリスト（週次）

- [ ] OpenAI使用量を確認（**目標: $3/月以下、上限$10/月**）
- [ ] UptimeRobotでダウンタイムを確認
- [ ] Sentryでエラー件数を確認
- [ ] Renderでリソース使用率を確認

### 💰 完全無料で運用するには

ハッカソン期間中（~3ヶ月）は以下で完全無料運用可能：

1. **OpenAI API**: 初回$5クレジット付与 → 慎重に使えば3ヶ月持つ
2. **Render**: Web Service 750時間/月無料（1アプリなら十分）
3. **PostgreSQL**: Render Free Tier 90日間 → その後はSupabase無料枠へ移行
4. **Vercel**: 完全無料（Hobby Plan）
5. **監視ツール**: 全て無料枠で十分

**3ヶ月後の選択肢**:
- PostgreSQL: [Supabase](https://supabase.com/) 無料枠（500MB）へ移行
- Render: 月$7で継続 or Heroku/Railway検討
- OpenAI: 使用量に応じて追加チャージ（$10-20/3ヶ月程度）

## 💰 コスト（学生ハッカソン想定）

### 初期3ヶ月（ハッカソン期間）

- **Vercel**: $0（完全無料）
- **Render Web Service**: $0（750時間/月無料、1アプリなら十分）
- **Render PostgreSQL**: $0（90日間無料）
- **OpenAI API**: $0-10/3ヶ月（初回$5クレジット + 慎重な使用で十分）
- **監視ツール**: $0（全て無料枠）

**合計: $0-10/3ヶ月**

### 3ヶ月後（継続運用する場合）

- **Vercel**: $0（引き続き無料）
- **Render Web Service**: $0または$7/月（無料枠継続 or Professional）
- **PostgreSQL**:
  - Render: $7/月
  - **推奨: Supabase無料枠へ移行**: $0（500MB、十分）
- **OpenAI API**: $3-10/月（使用量による）

**合計: $3-17/月**（Supabase移行なら$3-10/月）

### 💡 コスト削減の重要ポイント

1. **OpenAI APIを節約**:

   ```python
   # backend/app/core/config.py で既に設定済み
   OPENAI_MODEL=gpt-4o-mini  # 最安モデル使用中
   SKILL_TREE_CACHE_MINUTES=10  # キャッシュで重複生成を防止
   ```

2. **レート制限を強化**（後で実装推奨）:
   - スキルツリー生成: 1ユーザー1カテゴリ1回まで
   - 問題生成: 1ユーザー1日5回まで

3. **PostgreSQL容量管理**:
   - 定期的に古いデータをクリーンアップ
   - 90日後はSupabase無料枠（500MB）へ移行

4. **Renderのスリープを活用**:
   - フリープランは15分非アクセスでスリープ
   - デモ発表時のみ起動でOK（UptimeRobotで自動起動）

## 🔄 更新デプロイ

1. `git push origin main`（またはdevelop）
2. Vercel/Renderが自動的に検知して再デプロイ
3. 環境変数の変更は手動でDashboardから

## 🔐 セキュリティチェックリスト

### セキュリティ

- [ ] JWT_SECRET_KEYは十分にランダムか（64文字以上推奨）
- [ ] ENCRYPTION_KEYはFernet.generate_key()で生成したものか
- [ ] ADMIN_API_KEYは推測不可能なランダム文字列か
- [ ] OPENAI_API_KEYは本番用のキーか
- [ ] GITHUB_CLIENT_SECRETは絶対に公開していないか
- [ ] BACKEND_CORS_ORIGINSは"\*"ではなく具体的なURLか
- [ ] PostgreSQLのパスワードは安全か
- [ ] .envファイルが.gitignoreに含まれているか

### 監視・アラート設定

- [ ] OpenAI使用量上限を設定したか（**学生: Hard: $10, Soft: $5推奨**）
- [ ] UptimeRobotでBackend/Frontend監視を設定したか
- [ ] Sentryを統合したか（SENTRY_DSN環境変数設定）
- [ ] Renderでアラート通知を有効化したか
- [ ] 週次監視の担当者・曜日を決めたか

## 📝 参考リンク

- [Vercel Documentation](https://vercel.com/docs)
- [Render Documentation](https://render.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/manual/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
