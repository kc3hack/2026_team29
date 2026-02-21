# ADR 013: Quest API エンドポイント設計

## ステータス

- [x] **決定**（Issue #53 + #65 にて確定）

## コンテキスト (課題と背景)

Issue #53 で `/quests` 配下の RESTful API を設計する際、以下の判断が必要になった。

1. クエストの CRUD（作成・更新・削除）を MVP に含めるか
2. 進捗管理エンドポイント（start/complete）の Request/Response 確定
3. `user_id` をリクエストボディから受け取るか、認証コンテキストから取得するか
4. フィルタリング・ページネーションの設計

## 決定 (Decision)

### 1. Quest の Write 操作（POST/PUT/DELETE）は別 Issue（管理者 API）に切り出す

クエストはユーザーが「演習メニューから選ぶ」リソースであり、
作成・更新・削除はすべて管理者操作に相当する。エンドユーザーが Quest を直接変更する用途はない。

MVP ではクエストの Read と進捗管理のみを実装し、Write 操作は管理者 API として別 Issue で扱う。
（ADR 006 の管理者 API 方針と整合）

### 2. `user_id` はボディから廃止 → JWT の `current_user.id` を使用（Issue #65）

当初の暫定実装では `{ "user_id": int }` をボディで受け取っていたが、
これは攻撃者が任意の `user_id` を指定して他人のクエスト進捗を操作できる **IDOR 脆弱性** を持つ。
Issue #65 で認証統合後、`user_id` はボディから削除し JWT の `current_user.id` から取得する。

### 3. フィルタリング・ページネーションの設計（develop #64 にて追加）

クエスト一覧 `GET /quests` に `difficulty`, `skip`, `limit` クエリパラメータを追加。

### 4. 確定エンドポイント仕様

#### Quest（Read のみ）

| Method | Path | 認証 | Status | 概要 |
|---|---|---|---|---|
| GET | `/quests` | 不要 | 200 | クエスト一覧取得（カテゴリ・difficulty フィルタ、ページネーション対応） |
| GET | `/quests/{quest_id}` | 不要 | 200 | クエスト詳細取得 |
| POST | `/quests` | - | - | **別 Issue**（管理者 API）|
| PUT | `/quests/{quest_id}` | - | - | **別 Issue**（管理者 API）|
| DELETE | `/quests/{quest_id}` | - | - | **別 Issue**（管理者 API）|

**GET /quests**
```
Query:    category (optional): web/ai/security/infrastructure/design/game
          difficulty (optional): 0-9
          skip (default=0)
          limit (default=50)
Response: [ { id, title, description, difficulty, category, is_generated, created_at } ]
```

**GET /quests/{quest_id}**
```
Response: { id, title, description, difficulty, category, is_generated, created_at }
Error:    404
```

#### QuestProgress（認証必須: JWT の current_user.id を使用）

| Method | Path | 認証 | Status | 概要 |
|---|---|---|---|---|
| POST | `/quests/{quest_id}/start` | **必須** | 201 | クエスト開始 |
| POST | `/quests/{quest_id}/complete` | **必須** | 200 | クエスト完了 |

**POST /quests/{quest_id}/start**
```
Request:  {} （ボディなし: user_id は JWT から取得）
Response: { id, quest_id, status="in_progress", started_at, completed_at=null }
Error:    401 (未認証)
          404 (quest not found)
          409 (既に開始済み: UniqueConstraint 違反)
```

**POST /quests/{quest_id}/complete**
```
Request:  {} （ボディなし: user_id は JWT から取得）
Response: { id, quest_id, status="completed", started_at, completed_at }
Error:    401 (未認証)
          404 (quest not found / 進捗が存在しない)
          400 (IN_PROGRESS でない: 未開始または既に完了済み)
```

**complete のエラーハンドリング方針**:
エンドポイント層で `get_quest_progress` を呼び、status が `IN_PROGRESS` でない場合に 400 を返す。
CRUD 関数（`complete_quest`）はステータス確認済みの前提で動作する。

<<<<<<< HEAD
#### GET /users/me/quest-progress（補完: ADR 011 / ADR 015 参照）

| Method | Path | 認証 | Status | 概要 |
|---|---|---|---|---|
| GET | `/users/me/quest-progress` | **必須** | 200 | 自分の全進捗一覧取得 |

```
Response: [ { id, quest_id, status, started_at, completed_at } ]
          ※ 空配列を返す（404にしない）
Error:    401 (未認証)
```

## 代替案との比較 (Options)

### user_id をボディで受け取る（暫定実装）← **却下**

- **Good**: 認証実装前の暫定として動作確認が容易。
- **Bad**: IDOR（Insecure Direct Object Reference）脆弱性。任意の user_id を指定可能。
  IPA「安全なウェブサイトの作り方」の認可チェック漏れに相当。

### user_id を JWT から取得（採用）← **採用**

- **Good**: 自分の進捗しか操作できないことを API レベルで保証。URL/ボディに user_id 不要。
- **Bad**: 認証実装（#59/#61）が前提になる。
=======
#### GET /users/{user_id}/quest-progress（補完）

クエスト進捗一覧の **Read** は User API（Issue #51）で実装済み。
`/quests/{quest_id}/start|complete` と補完的に設計。

## 代替案との比較 (Options)

### Quest Write 操作を MVP に含める

- **Good**: Swagger UI でクエストデータを直接投入できる
- **Bad**: 管理者権限の認証が必要（Issue #53 では認証は後回し方針）。AI生成との統合も別 Issue。
  ユーザーがクエストを削除・編集するユースケースが存在しない。

### QuestProgress レスポンスに user_id を含める

```python
class QuestProgressResponse(BaseModel):
    id: int
    user_id: int   # 追加
    quest_id: int
    status: QuestStatus
    started_at: datetime | None
    completed_at: datetime | None
```

- **Good**: レスポンスが自己完結する
- **Bad**: ADR 011 と同様に専用レスポンススキーマ作成コストが生じる。既存 `QuestProgress` スキーマを流用できない。

→ **MVP では既存 `QuestProgress` スキーマを流用**（ADR 011 方針と統一）
>>>>>>> origin/develop

## 結果 (Consequences)

### Positive

<<<<<<< HEAD
- start/complete エンドポイントに IDOR 脆弱性がなくなる
- フロントは user_id を管理・送信する必要がなくなる

### Negative

- 認証なしでの動作確認ができなくなる（テストは JWT fixture が必要）

## 関連

- Issue #53: Quest API 実装
- Issue #65: Quest 進捗エンドポイント認証統合
- ADR 006: 管理者 API 認証方針
- ADR 013: Quest API（本 ADR）
- ADR 014: JWT 認証セッション管理
- ADR 015: `/users/me` エンドポイント移行方針

## 変更履歴

- 2026-02-20: 初版決定（Issue #53 設計議論）
- 2026-02-20: Issue #65 対応により `user_id` ボディ廃止を確定
=======
- スコープが明確になり、ハッカソン期間内に確実に完成できる
- 既存スキーマ（`QuestProgress`）をそのまま流用でき実装が高速
- 管理者 API を別 Issue で独立して設計・レビューできる

### Negative

- Swagger UI でのテストデータ投入は別 Issue 完了まで DB 直接操作が必要
- `user_id` をリクエストボディで受け取る仮実装のため、認証実装後に修正が必要

## 関連

- Issue #53: Quest API エンドポイント実装
- Issue #51: User API（`GET /users/{user_id}/quest-progress` 実装済み）
- ADR 006: 管理者 API 認証方針
- ADR 011: User API エンドポイント設計（スキーマ流用方針）
- ADR 012: Quest description Markdown 保存

## 変更履歴

- 2026-02-20: 決定（Issue #53 設計議論）
>>>>>>> origin/develop
