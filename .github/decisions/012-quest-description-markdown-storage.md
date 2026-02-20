# ADR 012: Quest の演習内容を Markdown Text 列に保存

## ステータス

- [x] **決定**

## コンテキスト (課題と背景)

Issue #53 で Quest API を設計する際、`description` フィールドに「演習手順・コードスニペット・ヒント」をどのように保存するかを決める必要があった。

演習内容は自然にステップ構造（概要 → 手順 → コード → 確認）を持つため、以下の選択肢が生じた。

- **構造化**（QuestStep テーブル、JSONB）で各要素を分割管理する
- **非構造化**（Markdown テキスト）で単一 Text 列に全て格納する

## 決定 (Decision)

`description` フィールド（`TEXT` 型）に Markdown 形式で演習内容を一括保存する。

```markdown
## 概要
Reactの基本を学ぶためのハンズオン演習

## 手順
### Step 1: プロジェクト作成
\`\`\`bash
npx create-react-app counter-app
\`\`\`
...
```

## 代替案との比較 (Options)

### 1. QuestStep テーブル（構造化）

```sql
CREATE TABLE quest_steps (
    id          SERIAL PRIMARY KEY,
    quest_id    INTEGER REFERENCES quests(id),
    step_order  INTEGER,
    content     TEXT,
    code_snippet TEXT
);
```

- **Good**: ステップ単位の進捗管理が可能（将来 Issue 化予定）。サーバー側でのコンテンツ操作が容易。
- **Bad**: テーブル追加・マイグレーション・CRUD・スキーマ全て新規設計が必要。ハッカソン期間内では過剰投資。

### 2. JSONB カラム

```python
description = Column(JSONB, nullable=False)
# 例: {"steps": [{"order": 1, "content": "...", "code": "..."}]}
```

- **Good**: 柔軟な構造を1カラムで表現できる。
- **Bad**: PostgreSQL 依存。テスト用 SQLite（in-memory）では `JSONB` 型が使えないため、テスト基盤（ADR 008 参照）と衝突する。また型定義・バリデーションが複雑になる。

## 結果 (Consequences)

### Positive

- SQLite / PostgreSQL 共通で動作し、既存のテスト基盤をそのまま使える
- スキーマ追加・マイグレーション不要で実装最速
- フロントエンドが Markdown パーサーで自由にレンダリングできる
- AI 生成クエスト（`is_generated=True`）も Markdown を直接生成・保存できる

### Negative

- サーバー側でのステップ単位フィルタ・検索が困難
- 将来 QuestStep テーブルへ移行する際にデータ変換マイグレーションが必要になる

## Future

ステップごとの進捗管理が必要になった段階で `QuestStep` テーブルの追加を別 Issue で検討する。
その時点で Markdown テキストから構造化データへの移行マイグレーションを実施する。

## 関連

- Issue #53: Quest API エンドポイント実装
- ADR 008: Alembicマイグレーション粒度（テスト用SQLite方針）
- ADR 013: Quest API エンドポイント設計

## 変更履歴

- 2026-02-20: 決定（Issue #53 設計議論）
