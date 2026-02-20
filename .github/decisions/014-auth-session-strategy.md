# ADR 014: 認証セッション管理方針（JWT vs Cookie Session）

## ステータス

- [x] **決定**

## コンテキスト (課題と背景)

Issue #59（GitHub OAuth 認証フロー実装）にて、OAuth コールバック後のセッション管理方針が未決定だった。

- GitHub OAuth で `code` を受け取りアクセストークンを取得した後、**フロントエンドとバックエンドの間でどのように認証状態を維持するか**を決める必要がある。
- この決定は以下に波及する:
  - `GET /auth/github/callback` のレスポンス形式
  - `app/dependencies/auth.py` の `get_current_user` 実装（Issue #61）
  - フロントエンドの API コール方式（Authorization ヘッダー vs Cookie の自動付与）

## 決定 (Decision)

**JWT (JSON Web Token) を Bearer トークンとして発行する。**

- `GET /auth/github/callback` のコールバック成功時に JWT を発行し、以下の形式でフロントに返す:
  ```
  GET /auth/github/callback
  → Redirect to: {FRONTEND_URL}/auth/callback?token=<jwt>
  ```
  もしくはレスポンスボディ:
  ```json
  { "access_token": "<jwt>", "token_type": "bearer" }
  ```
- フロントエンドは JWT を `localStorage` または `sessionStorage` に保存し、以降のリクエストに `Authorization: Bearer <jwt>` ヘッダーを付与する。
- JWT ペイロードには `user_id`, `sub` (github_user_id), `exp` (有効期限) を含める。
- `get_current_user` 依存関数（Issue #61）は `Authorization` ヘッダーからトークンを取得・検証する。

### JWT の設定値

| 設定項目 | 値 |
|---------|---|
| アルゴリズム | HS256 |
| 有効期限 | 24時間（ハッカソン用途のため長め） |
| 署名シークレット | 環境変数 `JWT_SECRET_KEY` |

## 代替案との比較 (Options)

### 1. Cookie Session（httpOnly Cookie）

- **Good**: XSS に強い（JS からアクセス不可），CSRF トークンと組み合わせれば安全。
- **Bad**: FastAPI での実装が複雑（`itsdangerous` や Redis 等のセッションストアが必要）。CORS + クレデンシャル付きリクエストの設定が煩雑。ハッカソン期間内の実装コストが高い。

### 2. JWT（Bearer Token）← **採用**

- **Good**: FastAPI の `python-jose` / `PyJWT` で簡単に実装可能。ステートレスでスケーラブル。`python-multipart` 不要。フロントの実装も `Authorization` ヘッダーを付けるだけで明確。
- **Bad**: `localStorage` 保存は XSS のリスクあり。トークン失効（ログアウト）はブラックリスト管理が必要だが MVP では省略可。

## セキュリティ上の注意事項

- `JWT_SECRET_KEY` は必ず `.env` で管理し、コードにハードコードしない。
- ロールアウト後（本番）では有効期限を短くし、リフレッシュトークン機構の追加を検討する。
- GitHub OAuth の `access_token`（暗号化保存済み、Issue #31）とアプリ発行 JWT は別物として管理する。

## 影響範囲

- `backend/app/api/endpoints/auth.py`（新規作成: Issue #59）
- `backend/app/dependencies/auth.py`（新規作成: Issue #61）
- `backend/app/core/config.py`（`JWT_SECRET_KEY` 追加）
- フロントエンドの API クライアント（全エンドポイントへのヘッダー付与）

## 参照

- Issue #59: GitHub OAuth 認証フロー実装
- Issue #61: 認証ミドルウェア実装
- ADR 005: OAuth トークン暗号化
