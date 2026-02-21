# ADR 016: GitHub OAuth 認証テスト戦略（外部API モック方針）

## ステータス

- [x] **決定**（Issue #59 テスト実装にて確定）

## コンテキスト (課題と背景)

Issue #59 で GitHub OAuth フロー（`GET /auth/github/login`, `GET /auth/github/callback`, `GET /auth/logout`）を実装した際、テスト戦略を決める必要があった。

GitHub OAuth フローのテストには以下の課題がある:

1. **外部API依存**: GitHub の認可ページ・トークンエンドポイント・ユーザー情報 API へのネットワーク接続が必要
2. **認可コードの使い捨て**: `code` パラメータは1回しか使えないため、繰り返し実行できない
3. **テスト用 OAuth App**: GitHub に登録した OAuth App の `client_id` / `client_secret` が必要
4. **CI/CD での実行**: シークレット管理・ネットワーク接続が CI 環境で不安定になりやすい
5. **httpOnly Cookie 検証**: `Set-Cookie` ヘッダーの `HttpOnly` フラグは TestClient でも確認可能

## 決定 (Decision)

**GitHub API への HTTP 通信を `unittest.mock` で完全にモック化し、実ネットワーク不要で検証する。**

### テスト構成

```
tests/test_api/test_auth.py  ← モックテスト（CI で常時実行）
```

```python
# httpx.Client を MagicMock で差し替え
with patch("app.api.endpoints.auth.httpx.Client", return_value=mock_client):
    res = client.get(f"/api/v1/auth/github/callback?code=...&state={state}")
```

### モックテストでカバーする項目

| テスト | 確認内容 |
|---|---|
| `test_login_redirects_to_github` | GitHub 認可 URL へのリダイレクト・`state` パラメータ存在 |
| `test_login_503_when_no_client_id` | `GITHUB_CLIENT_ID` 未設定時の 503 |
| `test_callback_new_user_creates_user_and_sets_cookie` | 新規登録 + JWT Cookie 発行 |
| `test_callback_new_user_username_collision` | username 重複時の ID サフィックス付与 |
| `test_callback_existing_user_updates_token` | 既存ユーザーの token 更新 |
| `test_callback_invalid_state_returns_400` | state 改ざん検知 400 |
| `test_callback_missing_state_returns_422` | state パラメータ欠落 422 |
| `test_callback_github_token_exchange_fails` | GitHub が access_token を返さない 400 |
| `test_callback_token_exchange_network_error` | ネットワーク障害でトークン交換失敗 502 |
| `test_callback_user_info_network_error` | トークン取得後に GitHub ユーザー情報取得でネットワークエラー 502 |
| `test_callback_token_exchange_http_status_error` | GitHub サーバーが 4xx/5xx を返す場合（`raise_for_status`）502 |
| `test_callback_redirect_location_is_frontend_url` | コールバック成功時のリダイレクト先が `FRONTEND_URL` |
| `test_logout_clears_cookie` | Cookie 削除（`max-age=0`）確認 |
| `test_logout_without_cookie_still_200` | Cookie なしでも 200 |
| `test_register_creates_account_and_sets_cookie` | 新規登録: 201 + JWT httpOnly Cookie 発行 |
| `test_register_duplicate_username_returns_409` | 同一 username の再登録 409 Conflict |
| `test_login_unknown_user_returns_401` | 存在しない username でログイン 401 |
| `test_login_existing_user_correct_password` | 正しいパスワードでログイン 200 |
| `test_login_existing_user_wrong_password` | 誤ったパスワードでログイン 401 |
| `test_login_github_oauth_user_denied` | GitHub OAuth ユーザーへの ID入力ログイン試行 401 （User Enumeration 防止） |
| `test_login_cookie_enables_authenticated_request` | ログイン Cookie で認証必須エンドポイントにアクセス可能 |

### モックテストで検証できないもの（手動確認が必要）

- GitHub 側の `client_id` / `client_secret` の正当性
- GitHub API の実際のレスポンス形式の変更
- 本番 HTTPS 環境での `Secure` Cookie フラグ動作
- CORS `allow_credentials=True` と実ブラウザの Cookie 自動送信

### 実際の OAuth フロー手動確認手順

```bash
# 1. GitHub OAuth App を登録（開発用）
#    Settings → Developer settings → OAuth Apps → New OAuth App
#    Authorization callback URL: http://localhost:8000/api/v1/auth/github/callback

# 2. .env に設定
GITHUB_CLIENT_ID=<取得した client_id>
GITHUB_CLIENT_SECRET=<取得した client_secret>
JWT_SECRET_KEY=$(openssl rand -hex 32)
FRONTEND_URL=http://localhost:3000

# 3. サーバー起動
docker compose up

# 4. ブラウザで確認
# → http://localhost:8000/api/v1/auth/github/login
# → GitHub 認可ページ → コールバック → localhost:3000 へリダイレクト
# → DevTools > Application > Cookies で確認:
#     access_token=<jwt>   HttpOnly: ✓   SameSite: Lax
```

### テスト用 JWT ヘルパー（`tests/conftest.py`）

認証が必要なエンドポイントのテスト用に、`Authorization: Bearer` ヘッダーフォールバックを利用する:

```python
from tests.conftest import auth_headers, make_test_token

# Bearer ヘッダーで認証済みリクエスト
res = client.get("/api/v1/users/me", headers=auth_headers(user_id))
```

`get_current_user` は Cookie → Bearer の順で検索するため、テストでは Bearer ヘッダーを使えば Cookie なしで認証済み状態を再現できる（ADR 014 参照）。

## 代替案との比較 (Options)

### 1. 実際の GitHub API を使う統合テスト

- **Good**: 本番に近い環境でフルフローを検証できる
- **Bad**: CI でシークレット管理が必要。`code` の使い捨て制約で自動化が困難。GitHub API レート制限にかかるリスク
- **却下理由**: ハッカソン期間中の CI 安定性を優先

### 2. モックサーバー（responses / respx）

- **Good**: `httpx` の実クライアントを使いつつ、ネットワーク通信だけを差し替えられる
- **Bad**: `respx` の追加依存が必要。`unittest.mock` より設定が複雑
- **却下理由**: `unittest.mock` で十分なカバレッジが得られる

### 3. モックテスト（採用）← **採用**

- **Good**: 追加依存なし。高速（2〜3秒）。CI で常時実行可能。フロー全体のロジックを検証
- **Bad**: GitHub API 仕様変更には追従できない（別途手動確認が必要）

## 関連

- Issue #59: GitHub OAuth 認証フロー実装
- ADR 010-b: スキルツリー API テスト戦略（外部API モックの先行事例）
- ADR 014: JWT 認証セッション管理方針（Bearer フォールバックの根拠）

## 変更履歴

- 2026-02-21: 初版決定（Issue #59 テスト実装）
- 2026-02-21: **変更**—テストカバレッジ表を最新化（Issue #59 レビュー対応）
  - ネットワークエラー系（502）・リダイレクト先検証・`register`/`login` 分離後のテストを追加
  - `test_login_github_oauth_user_denied`: 期待値を 403 → 401 に変更（ADR 017 変更に追従）
