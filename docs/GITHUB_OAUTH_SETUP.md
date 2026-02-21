# GitHub OAuth App セットアップガイド

このガイドでは、GitHub OAuthを使った認証機能を有効にするための設定手順を説明します。

## 前提条件

- GitHubアカウント
- アプリケーションのローカル開発環境（バックエンド: `http://localhost:8000`, フロントエンド: `http://localhost:3000`）

## 手順

### 1. GitHub OAuth Appの作成

1. GitHubにログインし、[Settings > Developer settings > OAuth Apps](https://github.com/settings/developers) にアクセスします
2. 「New OAuth App」ボタンをクリック
3. 以下の情報を入力：
   - **Application name**: `Team29 Skill Tree (Development)` (任意の名前)
   - **Homepage URL**: `http://localhost:3000`
   - **Application description**: (任意)
   - **Authorization callback URL**: `http://localhost:8000/api/v1/auth/github/callback`

4. 「Register application」ボタンをクリック

### 2. Client IDとClient Secretの取得

1. 作成したOAuth Appのページで、**Client ID**が表示されます（コピーしておく）
2. 「Generate a new client secret」ボタンをクリック
3. 表示された**Client Secret**をコピー（⚠️ このページを離れると二度と表示されません）

### 3. 環境変数の設定

`backend/.env` ファイルを編集し、以下の値を設定します：

```dotenv
# GitHub OAuth (本番設定)
GITHUB_CLIENT_ID=<先ほどコピーしたClient ID>
GITHUB_CLIENT_SECRET=<先ほどコピーしたClient Secret>
```

**例**:

```dotenv
GITHUB_CLIENT_ID=Iv1.a1b2c3d4e5f6g7h8
GITHUB_CLIENT_SECRET=1234567890abcdef1234567890abcdef12345678
```

### 4. 動作確認

1. バックエンドサーバーを再起動：

   ```bash
   cd backend
   poetry run uvicorn app.main:app --reload
   ```

2. フロントエンドサーバーを起動（別ターミナル）：

   ```bash
   cd frontend
   npm run dev
   ```

3. ブラウザで `http://localhost:3000/login` にアクセス

4. 「🚀 GitHub でログイン（推奨）」ボタンをクリック

5. GitHubの認可ページが表示されたら成功です

6. 「Authorize」をクリックすると、ダッシュボードにリダイレクトされます

## トラブルシューティング

### エラー: "GitHub OAuth は設定されていません"

- `.env` ファイルの `GITHUB_CLIENT_ID` と `GITHUB_CLIENT_SECRET` が正しく設定されているか確認
- バックエンドサーバーを再起動

### エラー: "Invalid or expired state parameter"

- CoWorks: `Authorization callback URL` が正しく設定されているか確認
- `http://localhost:8000/api/v1/auth/github/callback` であることを確認

### エラー: "The redirect_uri MUST match the registered callback URL"

- GitHub OAuth Appの設定で、**Authorization callback URL** が `http://localhost:8000/api/v1/auth/github/callback` であることを確認
- URLの末尾にスラッシュ `/` がないことを確認

## 本番環境への展開

本番環境では、以下のURLで新しいOAuth Appを作成してください：

- **Homepage URL**: `https://your-production-domain.com`
- **Authorization callback URL**: `https://your-api-domain.com/api/v1/auth/github/callback`

本番用の `GITHUB_CLIENT_ID` と `GITHUB_CLIENT_SECRET` を本番サーバーの環境変数に設定します。

## セキュリティ上の注意事項

⚠️ **Client Secret は絶対に Git にコミットしないでください**

- `.env` ファイルは `.gitignore` に含まれています
- 本番環境では環境変数またはシークレット管理サービス（AWS Secrets Manager, GitHub Secrets等）を使用してください
- Client Secret が漏洩した場合は、すぐにGitHub OAuth Appの設定から「Regenerate secret」を実行してください
