# ADR 011: User API エンドポイント設計

## ステータス

- [x] **決定**

## コンテキスト (課題と背景)

Issue #51 で `/users` 配下の RESTful API を設計する際、以下の判断が必要になった。

1. ネストされたリソース（Badge, SkillTree 等）のレスポンスに `user_id` を含めるか
2. 各エンドポイントの Request / Response の確定

## 決定 (Decision)

### 1. ネストリソースの `user_id` は含めたまま（MVP優先）

`GET /users/{user_id}/badges` 等のレスポンスに `user_id` を含める。
クライアントはパスから `user_id` を知っているため技術的には冗長だが、以下の理由でMVPでは含める。

- 既存スキーマ（`Badge`, `SkillTree`, `QuestProgress`）をそのまま流用できる
- 別途 `BadgeResponse`（user_id なし）等のスキーマを作るコストを避ける
- フロントが無視すれば実害なし

**Future**: API 公開・外部連携が必要になった段階で専用レスポンススキーマへ切り出しを検討。

### 2. 確定エンドポイント仕様

#### User

| Method | Path | Status | 概要 |
|---|---|---|---|
| POST | `/users` | 201 | ユーザー登録（仮実装・username のみ） |
| GET | `/users/{user_id}` | 200 | ユーザー情報取得 |
| PUT | `/users/{user_id}` | 200 | username 更新のみ（ADR 010参照） |
| DELETE | `/users/{user_id}` | 204 | ユーザー削除 |

**POST /users**
```
Request:  { "username": "string" }
Response: { id, username, level=1, exp=0, rank=0, created_at, updated_at }
Error:    400 username重複
Note:     SkillTree 6カテゴリが自動初期化される（CRUD層実装済み）
```

**GET /users/{user_id}**
```
Response: { id, username, level, exp, rank, created_at, updated_at }
Error:    404
```

**PUT /users/{user_id}**
```
Request:  { "username"?: "string" }
          ※ level / exp / rank はサーバー管理のため除外（ADR 010）
Response: { id, username, level, exp, rank, created_at, updated_at }
Error:    404
```

**DELETE /users/{user_id}**
```
Response: 204 No Content
Error:    404
```

#### Profile

| Method | Path | Status | 概要 |
|---|---|---|---|
| GET | `/users/{user_id}/profile` | 200 | プロフィール取得 |
| PUT | `/users/{user_id}/profile` | 200 | プロフィール更新（Upsert） |

**GET /users/{user_id}/profile**
```
Response: { id, user_id, github_username, qiita_id, connpass_id,
            portfolio_url, portfolio_text, last_analyzed_at }
Error:    404 (user not found / profile not found)
```

**PUT /users/{user_id}/profile**
```
Request:  { "github_username"?: str, "qiita_id"?: str, "connpass_id"?: str,
            "portfolio_url"?: str, "portfolio_text"?: str }  ← 全て optional
Response: { id, user_id, github_username, qiita_id, connpass_id,
            portfolio_url, portfolio_text, last_analyzed_at }
Error:    404 (user not found)
Note:     profile が存在しない場合は作成（Upsert）
```

#### Badge

| Method | Path | Status | 概要 |
|---|---|---|---|
| GET | `/users/{user_id}/badges` | 200 | バッジ一覧取得 |

**GET /users/{user_id}/badges**
```
Response: [ { id, user_id, category, tier, earned_at } ]
          ※ user_id は冗長だが MVP では既存スキーマを流用
          ※ 空配列を返す（404にしない）
Error:    404 (user not found)
```

#### SkillTree

| Method | Path | Status | 概要 |
|---|---|---|---|
| GET | `/users/{user_id}/skill-trees` | 200 | スキルツリー一覧取得 |

**GET /users/{user_id}/skill-trees**
```
Response: [ { id, user_id, category, tree_data, generated_at } ]
          ※ ユーザー作成時に6カテゴリ自動初期化のため必ず6件
Error:    404 (user not found)
```

#### QuestProgress

| Method | Path | Status | 概要 |
|---|---|---|---|
| GET | `/users/{user_id}/quest-progress` | 200 | クエスト進捗一覧取得 |

**GET /users/{user_id}/quest-progress**
```
Response: [ { id, user_id, quest_id, status, started_at, completed_at } ]
          ※ 空配列を返す（404にしない）
Error:    404 (user not found)
```

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

- レスポンスに冗長な `user_id` が含まれる
  - **対処法**: Future で専用レスポンススキーマへ切り出す

## 関連

- Issue #51: User API エンドポイント実装
- ADR 010: rankフィールドの管理方針（PUT /users/{id} の設計判断）

## 変更履歴

- 2026-02-20: 決定（Issue #51 設計議論）
