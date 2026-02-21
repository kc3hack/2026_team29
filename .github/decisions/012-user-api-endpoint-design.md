# ADR 011: User API エンドポイント設計

## ステータス

- [x] **決定**（ADR 015 にて `/users/me` 移行を決定 — 本 ADR の仕様は部分的に更新済み）

## コンテキスト (課題と背景)

Issue #51 で `/users` 配下の RESTful API を設計する際、以下の判断が必要になった。

1. ネストされたリソース（Badge, SkillTree 等）のレスポンスに `user_id` を含めるか
2. 各エンドポイントの Request / Response の確定

## 決定 (Decision)

### 1. ネストリソースの `user_id` を除去（コミット eaed96e）

当初は既存スキーマを流用して `user_id` を含める方針だったが、
その後のリファクタリング（eaed96e）でレスポンススキーマから冗長な `user_id` を除去した。

除去した理由:
- クライアントはパスから `user_id` を知っているため不要
- RESTful 的に冗長情報を排除

**Future**: API 公開・外部連携が必要になった段階で専用レスポンススキーマへ切り出しを検討。

### 2. 確定エンドポイント仕様（ADR 015 による更新後）

> **⚠️ 更新**: Issue #59 にて `POST /users` および `GET/PUT/DELETE /users/{user_id}` 系を削除済み。
> ユーザー登録経路は `POST /auth/register` に一本化（ADR 017 参照）。
> 旧 `/users/{user_id}` 仕様は ADR 015 参照。

#### 認証（ユーザー登録・ログイン）

| Method | Path | 認証 | Status | 概要 |
|---|---|---|---|---|
| POST | `/auth/register` | 不要 | 201 | username+password 新規登録（username 重複: 409） |
| POST | `/auth/login` | 不要 | 200 | username+password ログイン（未登録/誤PW: 401） |
| GET | `/auth/github/login` | 不要 | 302 | GitHub OAuth ログイン開始 |
| GET | `/auth/github/callback` | 不要 | 302 | GitHub OAuth コールバック → JWT Cookie 発行 |
| POST | `/auth/logout` | 不要 | 200 | httpOnly Cookie 削除 |

#### User

| Method | Path | 認証 | Status | 概要 |
|---|---|---|---|---|
| GET | `/users/me` | **必須** | 200 | 自分のユーザー情報取得 |
| PUT | `/users/me` | **必須** | 200 | username 更新のみ（ADR 010参照） |
| DELETE | `/users/me` | **必須** | 204 | 自分のアカウント削除 |
| ~~POST~~ | ~~`/users`~~ | - | - | **削除済み**（Issue #59 で廃止、`POST /auth/register` に一本化） |
| ~~GET/PUT/DELETE~~ | ~~`/users/{user_id}`~~ | - | - | **削除済み**（管理者 API として別 Issue で再実装予定） |

**GET /users/me** （要 Cookie `access_token` / または `Authorization: Bearer <token>`。ADR 014 参照）
```
Response: { id, username, level, exp, rank, created_at, updated_at }
Error:    401 (トークンなし/不正), 404 (ユーザー削除済み)
```

**PUT /users/me** （要 Cookie `access_token` / または `Authorization: Bearer <token>`）
```
Request:  { "username"?: "string" }
          ※ level / exp / rank はサーバー管理のため除外（ADR 010）
Response: { id, username, level, exp, rank, created_at, updated_at }
Error:    401, 400 (username重複), 404
```

**DELETE /users/me** （要 Cookie `access_token` / または `Authorization: Bearer <token>`）
```
Response: 204 No Content
Error:    401, 404
```

#### Profile

| Method | Path | 認証 | Status | 概要 |
|---|---|---|---|---|
| GET | `/users/me/profile` | **必須** | 200 | 自分のプロフィール取得 |
| PUT | `/users/me/profile` | **必須** | 200 | 自分のプロフィール更新（Upsert） |
| ~~GET~~ | ~~`/users/{user_id}/profile`~~ | - | - | **削除済み**（管理者 API として別 Issue で再実装予定） |

**GET /users/me/profile** （要 Cookie `access_token` / または `Authorization: Bearer <token>`）
```
Response: { id, user_id, github_username, qiita_id, connpass_id,
            portfolio_url, portfolio_text, last_analyzed_at }
Error:    401, 404 (profile not found)
```

**PUT /users/me/profile**
```
Request:  { "github_username"?: str, "qiita_id"?: str, "connpass_id"?: str,
            "portfolio_url"?: str, "portfolio_text"?: str }  ← 全て optional
Response: { id, user_id, github_username, qiita_id, connpass_id,
            portfolio_url, portfolio_text, last_analyzed_at }
Error:    401
Note:     profile が存在しない場合は作成（Upsert）
```

#### Badge / SkillTree / QuestProgress

| Method | Path | 認証 | Status | 概要 |
|---|---|---|---|---|
| GET | `/users/me/badges` | **必須** | 200 | 自分のバッジ一覧 |
| GET | `/users/me/skill-trees` | **必須** | 200 | 自分のスキルツリー一覧 |
| GET | `/users/me/quest-progress` | **必須** | 200 | 自分のクエスト進捗一覧 |
| ~~GET~~ | ~~`/users/{user_id}/badges`~~ | - | - | **削除済み**（管理者 API として別 Issue で再実装予定） |
| ~~GET~~ | ~~`/users/{user_id}/skill-trees`~~ | - | - | **削除済み**（管理者 API として別 Issue で再実装予定） |
| ~~GET~~ | ~~`/users/{user_id}/quest-progress`~~ | - | - | **削除済み**（管理者 API として別 Issue で再実装予定） |

## 代替案との比較 (Options)

### ネストリソースから user_id を除外する

```python
class BadgeResponse(BaseModel):
    id: int
    category: BadgeCategory
    tier: int
    earned_at: datetime
    # user_id は除外
```

- **Good**: RESTful 的に冗長情報を排除、ペイロード削減
- **Bad**: 既存 `Badge` スキーマと別に `BadgeResponse` を作る必要がある。全リソース分（Badge, SkillTree, QuestProgress）で作業が増える
- **却下理由**: MVP のスピード感に合わない。フロントが無視すれば実害なし

## 結果 (Consequences)

### Positive

- 既存スキーマをそのまま流用でき、実装が高速
- エンドポイント仕様が ADR として記録され、チーム内で認識統一

### Negative

- **後方互換 `/users/{user_id}` の読み取りは認証不要** のため、ユーザー情報が公開状態。
  管理者 API（ADR 006）に移行後は削除または認証付きに変更予定。

## 関連

- Issue #51: User API エンドポイント実装
- Issue #61: 認証ミドルウェア実装と /users 統合
- ADR 010: rankフィールドの管理方針（PUT /users/me の設計判断）
- ADR 014: JWT 認証セッション管理方針
- ADR 015: `/users/me` エンドポイント移行方針（本 ADR の仕様変更を記録）

## 変更履歴

- 2026-02-20: 初版決定（Issue #51 設計議論）
- 2026-02-20: ADR 015 に基づき `/users/{user_id}` → `/users/me` に更新（Issue #61）
- 2026-02-21: Issue #59 refactor にて以下を削除済みとして更新
  - `POST /users` → 廃止。`POST /auth/register` が新規登録の正式経路（ADR 017）
  - `GET/PUT/DELETE /users/{user_id}` および `/{user_id}/profile` 等 → 削除済み（管理者 API として別 Issue で再実装予定）
  - 認証エンドポイント表を新規追加（ADR 014 / ADR 017 の仕様を集約）
