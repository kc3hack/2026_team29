# ADR 013: Quest API エンドポイント設計

## ステータス

- [x] **決定**

## コンテキスト (課題と背景)

Issue #53 で `/quests` 配下の RESTful API を設計する際、以下の判断が必要になった。

1. クエストの CRUD（作成・更新・削除）を MVP に含めるか
2. 進捗管理エンドポイント（start/complete）の Request/Response 確定
3. フィルタリング・ページネーションの設計

## 決定 (Decision)

### 1. Quest の Write 操作（POST/PUT/DELETE）は別 Issue（管理者 API）に切り出す

クエストはユーザーが「演習メニューから選ぶ」リソースであり、
作成・更新・削除はすべて管理者操作に相当する。エンドユーザーが Quest を直接変更する用途はない。

MVP ではクエストの Read と進捗管理のみを実装し、Write 操作は管理者 API として別 Issue で扱う。
（ADR 006 の管理者 API 方針と整合）

### 2. 確定エンドポイント仕様

#### Quest（Read のみ）

| Method | Path | Status | 概要 |
|---|---|---|---|
| GET | `/quests` | 200 | クエスト一覧取得（フィルタ・ページネーション） |
| GET | `/quests/{quest_id}` | 200 | クエスト詳細取得 |
| POST | `/quests` | - | **別 Issue**（管理者 API）|
| PUT | `/quests/{quest_id}` | - | **別 Issue**（管理者 API）|
| DELETE | `/quests/{quest_id}` | - | **別 Issue**（管理者 API）|

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

#### QuestProgress

| Method | Path | Status | 概要 |
|---|---|---|---|
| POST | `/quests/{quest_id}/start` | 201 | クエスト開始 |
| POST | `/quests/{quest_id}/complete` | 200 | クエスト完了 |

**POST /quests/{quest_id}/start**
```
Request:  { "user_id": int }  ※ 認証実装後は JWT から取得
Response: { id, quest_id, status="in_progress", started_at, completed_at=null }
Error:    404 (quest not found)
          409 (既に開始済み: UniqueConstraint 違反)
```

**POST /quests/{quest_id}/complete**
```
Request:  { "user_id": int }  ※ 認証実装後は JWT から取得
Response: { id, quest_id, status="completed", started_at, completed_at }
Error:    404 (quest not found)
          400 (IN_PROGRESS でない: 未開始または既に完了済み)
```

**complete のエラーハンドリング方針**:
エンドポイント層で `get_quest_progress` を呼び、status が `IN_PROGRESS` でない場合に 400 を返す。
CRUD 関数（`complete_quest`）はステータス確認済みの前提で動作する。

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

## 結果 (Consequences)

### Positive

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
