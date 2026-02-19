# ADR 008: Alembicマイグレーション粒度（テーブル単位分離 vs 一括マイグレーション）

## ステータス

- [x] **決定**

## コンテキスト (課題と背景)

issue #31で6テーブル（Profile, OAuthAccount, Badge, Quest, QuestProgress, SkillTree）を実装する際、Alembicマイグレーションファイルをどの粒度で作成するか検討しました:

- **ロールバック戦略**: スキーマ変更を元に戻す際、どの単位で巻き戻すべきか
- **依存関係管理**: テーブル間の外部キー制約による依存順序を明確にする必要がある
- **保守性**: マイグレーションファイルが増えると管理コストが上がる
- **デバッグ**: マイグレーション失敗時に、どのテーブルで問題が起きたか特定しやすくしたい

## 決定 (Decision)

**テーブル単位でマイグレーションを分離**する（6本のマイグレーションファイル）:

```
依存順序:
0002_create_profiles_table.py
0003_create_oauth_accounts_table.py (depends on: users)
0004_create_badges_table.py (depends on: users)
0005_create_quests_table.py (standalone)
0006_create_quest_progress_table.py (depends on: users, quests)
0007_create_skill_trees_table.py (depends on: users)
```

### 実装原則

- **1テーブル = 1マイグレーション**: 各テーブルごとに独立したマイグレーションファイル
- **依存順序を明示**: `down_revision` で前のマイグレーションに依存
- **ロールバック単位**: テーブル単位で巻き戻し可能
- **命名規則**: `000X_create_{table_name}_table.py` で統一

## 代替案との比較 (Options)

### 1. 一括マイグレーション（全6テーブルを1ファイルにまとめる）

```python
# 0002_create_all_tables.py
def upgrade() -> None:
    op.create_table("profiles", ...)
    op.create_table("oauth_accounts", ...)
    op.create_table("badges", ...)
    op.create_table("quests", ...)
    op.create_table("quest_progress", ...)
    op.create_table("skill_trees", ...)
```

- **Good**:
  - マイグレーションファイル数が少ない（1ファイルで完結）
  - 全テーブルを一度にデプロイできる
- **Bad**:
  - ロールバック時に個別テーブル単位で戻せない（all-or-nothing）
  - マイグレーション失敗時、どのテーブルで問題が起きたか特定しづらい
  - テーブル追加時の依存関係が複雑化（外部キー制約の順序管理が煩雑）
  - **却下理由**: ロールバック粒度が粗すぎる、デバッグが困難

### 2. 機能単位でグループ化（User関連、Quest関連等）

```python
# 0002_create_user_related_tables.py
def upgrade() -> None:
    op.create_table("profiles", ...)
    op.create_table("oauth_accounts", ...)
    op.create_table("skill_trees", ...)

# 0003_create_quest_related_tables.py
def upgrade() -> None:
    op.create_table("quests", ...)
    op.create_table("quest_progress", ...)
```

- **Good**:
  - 機能単位でロールバック可能（User機能全体を戻す等）
  - ファイル数が適度（2-3ファイル）
- **Bad**:
  - 機能グループの境界が曖昧（Badgeはどちらに属するか？）
  - 1ファイル内の複数テーブルで失敗した場合、デバッグが困難
  - **却下理由**: グループ分けの基準が不明確、保守性が低い

### 3. カラム変更も含めて細かく分離（カラム単位）

```python
# 0002_create_profiles_table.py
# 0003_add_github_username_to_profiles.py
# 0004_add_qiita_id_to_profiles.py
```

- **Good**: 変更履歴が細かく記録される
- **Bad**:
  - マイグレーションファイル数が爆発的に増える
  - 新規テーブル作成時に細分化する意味がない
  - **却下理由**: オーバーエンジニアリング

## 結果 (Consequences)

### Positive

- **ロールバック粒度の細かさ**: テーブル単位で巻き戻し可能（例: SkillTreeだけロールバック）
- **デバッグ容易性**: マイグレーション失敗時、どのテーブルで問題が起きたか特定しやすい
- **依存関係の明確化**: `down_revision` で依存順序が明示される
- **段階的デプロイ**: 必要に応じてテーブルごとに段階的にデプロイ可能

### Negative

- **マイグレーションファイル数の増加**: 6テーブル分のファイル管理が必要
  - **対処法**: 命名規則（`000X_create_{table_name}_table.py`）で整理
- **管理コスト微増**: ファイル数が増えることで、全体の把握が若干困難
  - **対処法**: ハッカソン規模（数十テーブル以下）では許容範囲

### 実装ガイドライン

- **新規テーブル追加時**: 1テーブル = 1マイグレーションファイルの原則を守る
- **カラム追加・変更時**: 別途マイグレーションファイルを作成（テーブル作成とは分離）
- **ロールバック手順**: `alembic downgrade -1` でテーブル単位で巻き戻し
- **Phase 2以降**: テーブル数が50を超えたら機能単位グループ化を検討
