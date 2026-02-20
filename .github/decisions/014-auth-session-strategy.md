# ADR 014: 認証セッション管理方針（JWT + httpOnly Cookie）

## ステータス

- [x] **決定**（初版: JWT レスポンスボディ返却 → 更新: httpOnly Cookie に変更）

## コンテキスト (課題と背景)

Issue #59（GitHub OAuth 認証フロー実装）にて、OAuth コールバック後のセッション管理方針が未決定だった。

- GitHub OAuth で `code` を受け取りアクセストークンを取得した後、**フロントエンドとバックエンドの間でどのように認証状態を維持するか**を決める必要がある。
- この決定は以下に波及する:
  - `GET /auth/github/callback` のレスポンス形式
  - `app/dependencies/auth.py` の `get_current_user` 実装（Issue #61）
  - フロントエンドの API コール方式（Authorization ヘッダー vs Cookie の自動付与）

## 決定 (Decision)

**JWT (HS256) を `httpOnly; Secure; SameSite=Lax` Cookie として発行する。**

### フロー

```
GET /auth/github/login
→ GitHub 認可ページへリダイレクト（HMAC 署名済み state 付き）

GET /auth/github/callback?code=xxx&state=xxx
→ state 検証 → code 交換 → GitHub ユーザー取得 → User 作成/照合
→ Set-Cookie: access_token=<jwt>; HttpOnly; Secure; SameSite=Lax; Path=/
→ 302 Redirect to: {FRONTEND_URL}

GET /auth/logout
→ Cookie を削除して返す
```

### なぜ `httpOnly Cookie` に変更したか

初版では JWT をレスポンスボディで返し、フロントが `localStorage` に保存する方針だったが、
`localStorage` はページ内 JS に完全公開されるため、**XSS によるトークン盗取が可能**。
`httpOnly` Cookie にすることで JS からのアクセスを OS レベルで禁止し、XSS 耐性を確保する。

### トークン取得優先順位（get_current_user）

```
1. Cookie `access_token`（httpOnly）      ← ブラウザ通常フロー
2. Authorization: Bearer <token> ヘッダー ← テスト / API クライアント互換
```

### JWT の設定値

| 設定項目 | 値 |
|---------|---|
| アルゴリズム | HS256 |
| 有効期限 | 24時間（ハッカソン用途のため長め） |
| 署名シークレット | 環境変数 `JWT_SECRET_KEY` |
| Cookie 名 | `access_token` |
| Cookie フラグ | `HttpOnly; SameSite=Lax; Secure`（localhost は `Secure=false`） |

## 代替案との比較 (Options)

### 1. JWT をレスポンスボディで返す（初版）← **却下**

- **Good**: 実装が単純。フロントが `localStorage` に保存してヘッダーに付ける。
- **Bad**: `localStorage` は XSS で完全に読み取り可能。トークン盗取リスクが高い。
  IPA「安全なウェブサイトの作り方」でも localStorage へのトークン保存を非推奨としている。

### 2. JWT + httpOnly Cookie ← **採用**

- **Good**: JS から Cookie にアクセス不可 → XSS によるトークン盗取を防止。
  `SameSite=Lax` により外部サイトからの自動送信を制限（CSRF 緩和）。
  FastAPI の `Response.set_cookie()` で実装が容易。
  フロントは Cookie を自動送信するため実装が単純になる。
- **Bad**: CORS 設定で `allow_credentials=True` かつ `*` 以外のオリジン指定が必要。
  `BACKEND_CORS_ORIGINS` と `FRONTEND_URL` を環境変数で正しく設定する必要がある。

### 3. サーバーサイドセッション（Redis + Cookie）

- **Good**: トークン即時失効が可能。セキュリティが最も高い。
- **Bad**: Redis が必要。ハッカソン期間内の実装コストが高い。ステートフル。

## セキュリティ上の注意事項

- `JWT_SECRET_KEY` は必ず `.env` で管理し、コードにハードコードしない。
- `SameSite=Lax` は CSRF の完全な防御ではない（GET リクエストでは Cookie が送信される）。
  Write 操作（POST/PUT/DELETE）では Cookie が送信されない外部サイトからは実質無効。
- ログアウト API（`GET /auth/logout`）は Cookie を削除するが、JWT 自体はサーバー側で無効化できない。
  有効期限内の悪用を防ぐには将来的にブラックリスト（Redis）対応が必要。
- `Secure` フラグ: `FRONTEND_URL` が `http://localhost` の場合は自動的に `false`（開発時のみ）。
  本番では必ず HTTPS を使用し `Secure=true` とすること。
- GitHub OAuth の `access_token`（暗号化保存済み、Issue #31）とアプリ発行 JWT は別物として管理する。

## 影響範囲

- `backend/app/api/endpoints/auth.py`（Cookie セット + logout エンドポイント追加）
- `backend/app/dependencies/auth.py`（Cookie → Authorization ヘッダーの順で検索）
- `backend/app/core/config.py`（`JWT_SECRET_KEY`, `FRONTEND_URL` 追加）
- `BACKEND_CORS_ORIGINS` に `FRONTEND_URL` を含める必要がある（Cookie の `credentials` 送信に必須）
- フロントエンド: `Authorization` ヘッダー付与が不要になる。`credentials: 'include'` を fetch に追加

## 参照

- Issue #59: GitHub OAuth 認証フロー実装
- Issue #61: 認証ミドルウェア実装
- ADR 005: OAuth トークン暗号化
- IPA「安全なウェブサイトの作り方」: localStorage へのトークン保存を非推奨

## 変更履歴

- 2026-02-20: 初版（JWT をレスポンスボディで返す Bearer Token 方式）
- 2026-02-21: httpOnly Cookie 方式に変更（XSS 対策強化）
