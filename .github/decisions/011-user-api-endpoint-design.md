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

> **⚠️ 更新**: Issue #61 / ADR 015 にて `/users/{user_id}` → `/users/me` に移行済み。
> 以下は **現行の実装** を反映。旧仕様との比較は ADR 015 参照。

#### User

| Method | Path | 認証 | Status | 概要 |
|---|---|---|---|---|
| POST | `/users` | 不要 | 201 | ユーザー登録（後方互換: OAuth後は `/auth/github/callback` が主経路） |
| GET | `/users/me` | **必須** | 200 | 自分のユーザー情報取得 |
| PUT | `/users/me` | **必須** | 200 | username 更新のみ（ADR 010参照） |
| DELETE | `/users/me` | **必須** | 204 | 自分のアカウント削除 |
| GET | `/users/{user_id}` | 不要 | 200 | ユーザー情報取得（後方互換 / 管理者用） |

**POST /users**
```
Request:  { "username": "string" }
Response: { id, username, level=1, exp=0, rank=0, created_at, updated_at }
Error:    400 username重複
Note:     SkillTree 6カテゴリが自動初期化される（CRUD層実装済み）
```

**GET /users/me** （要 Authorization: Bearer <token>）
```
Response: { id, username, level, exp, rank, created_at, updated_at }
Error:    401 (トークンなし/不正), 404 (ユーザー削除済み)
```

**PUT /users/me** （要 Authorization: Bearer <token>）
```
Request:  { "username"?: "string" }
          ※ level / exp / rank はサーバー管理のため除外（ADR 010）
Response: { id, username, level, exp, rank, created_at, updated_at }
Error:    401, 400 (username重複), 404
```

**DELETE /users/me** （要 Authorization: Bearer <token>）
```
Response: 204 No Content
Error:    401, 404
```

#### Profile

| Method | Path | 認証 | Status | 概要 |
|---|---|---|---|---|
| GET | `/users/me/profile` | **必須** | 200 | 自分のプロフィール取得 |
| PUT | `/users/me/profile` | **必須** | 200 | 自分のプロフィール更新（Upsert） |
| GET | `/users/{user_id}/profile` | 不要 | 200 | プロフィール取得（後方互換 / 管理者用） |

**GET /users/me/profile**
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
| GET | `/users/{user_id}/badges` | 不要 | 200 | バッジ一覧（後方互換 / 管理者用） |
| GET | `/users/{user_id}/skill-trees` | 不要 | 200 | スキルツリー（後方互換 / 管理者用） |
| GET | `/users/{user_id}/quest-progress` | 不要 | 200 | 進捗一覧（後方互換 / 管理者用） |

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
