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

## 📊 モニタリング

- **Render Logs**: Dashboard → Logs
- **Vercel Logs**: Dashboard → Deployments → Logs
- **エラートラッキング**: RenderのMetricsタブで確認

## 💰 コスト

- **Vercel**: フリープラン（Hobby）
- **Render**:
  - Web Service: フリープラン（750時間/月、スリープあり）
  - PostgreSQL: フリープラン（90日間、その後$7/月）

## 🔄 更新デプロイ

1. `git push origin main`（またはdevelop）
2. Vercel/Renderが自動的に検知して再デプロイ
3. 環境変数の変更は手動でDashboardから

## 🔐 セキュリティチェックリスト

- [ ] JWT_SECRET_KEYは十分にランダムか（64文字以上推奨）
- [ ] ENCRYPTION_KEYはFernet.generate_key()で生成したものか
- [ ] ADMIN_API_KEYは推測不可能なランダム文字列か
- [ ] OPENAI_API_KEYは本番用のキーか
- [ ] GITHUB_CLIENT_SECRETは絶対に公開していないか
- [ ] BACKEND_CORS_ORIGINSは"\*"ではなく具体的なURLか
- [ ] PostgreSQLのパスワードは安全か
- [ ] .envファイルが.gitignoreに含まれているか

## 📝 参考リンク

- [Vercel Documentation](https://vercel.com/docs)
- [Render Documentation](https://render.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/manual/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
