# ADR 015: `/users/me` エンドポイント移行方針

## ステータス

- [x] **決定**

## コンテキスト (課題と背景)

- ADR 011 で `/users/{user_id}` を採用してエンドポイントを仮実装した（Issue #51）。
- Issue #59（GitHub OAuth）実装後、認証済みユーザーの操作は「URL の `user_id` を使う案（B）」か
  「`/users/me` で認証コンテキストから解決する案（A）」かを決定する必要がある（Issue #61）。
- Issue #65 の Quest 進捗エンドポイントも同様に `user_id` をボディから廃止する必要があり、
  `/users/me` 方針と整合させる必要がある。

## 決定 (Decision)

**案 A: `/users/me` を採用する（認証コンテキストから `user_id` を解決）**

### 変更後のエンドポイント仕様（ADR 011 更新分）

| 変更前 | 変更後 | 概要 |
|--------|--------|------|
| `GET /users/{user_id}` | `GET /users/me` | 自分のユーザー情報取得 |
| `PUT /users/{user_id}` | `PUT /users/me` | username 更新（自分のみ） |
| `DELETE /users/{user_id}` | `DELETE /users/me` | 自分のアカウント削除 |
| `GET /users/{user_id}/profile` | `GET /users/me/profile` | 自分のプロフィール取得 |
| `PUT /users/{user_id}/profile` | `PUT /users/me/profile` | 自分のプロフィール更新 |

> **例外**: 管理者が他ユーザーを操作する場合は `/users/{user_id}` を維持（管理者 API: ADR 006 参照）

### Quest 進捗エンドポイントへの適用（Issue #65）

```python
# Before (危険: 任意の user_id を指定可能)
POST /quests/{quest_id}/start    { "user_id": int }
POST /quests/{quest_id}/complete { "user_id": int }

# After (JWT の current_user.id を使用)
POST /quests/{quest_id}/start    {}  # ボディの user_id を廃止
POST /quests/{quest_id}/complete {}  # ボディの user_id を廃止
```

## 代替案との比較 (Options)

### 案 A: `/users/me`（認証コンテキスト解決）← **採用**

- **Good**: URL に `user_id` が露出しない。他ユーザーへの横断アクセスを URL レベルで防止可能。
  GitHub API / Twitter API / Discord API など主要 SaaS の採用実績あり。フロントが `user_id` を保持不要。
- **Bad**: 厳密な REST の「リソース識別子は URL に」という原則から外れる（実用上は許容範囲）。

### 案 B: `/users/{user_id}` + 認証検証

- **Good**: RESTful の慣習に忠実。管理者による他ユーザー操作と同じ形式で一貫性がある。
- **Bad**: フロントが `user_id` をストレージに保持する必要がある。ミドルウェアで `URL の user_id == JWT の user_id` の一致検証を毎回行う必要があり実装コストが高い。

## 移行方針（実装手順）

1. **Issue #61 で対応**:
   - `GET/PUT/DELETE /users/{user_id}` → `GET/PUT/DELETE /users/me` に変更
   - `get_current_user` 依存関数を各エンドポイントに注入
   - 既存テストの fixture を認証ヘッダー付きに更新
2. **Issue #65 で対応**:
   - `QuestProgressStart` / `QuestProgressComplete` スキーマから `user_id` フィールド削除
   - `current_user.id` で置き換え

## フロントエンドへの影響（要共有）

- APIクライアントの全 `/users/{user_id}` 呼び出しを `/users/me` に変更する必要がある。
- ストレージに `user_id` を保持している箇合は不要になる（JWT デコードまたはサーバーから取得）。
- Quest の `start`/`complete` API の Request Body から `user_id` を削除する。

## 参照

- ADR 011: User API エンドポイント設計（本 ADR により部分更新）
- ADR 013: Quest API エンドポイント設計（`user_id` ボディ廃止）
- ADR 014: JWT 認証セッション管理
- Issue #59: GitHub OAuth 認証フロー実装
- Issue #61: 認証ミドルウェア実装
- Issue #65: Quest 進捗エンドポイント認証統合
