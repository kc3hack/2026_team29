# ADR 008: Alembicマイグレーション粒度（issue単位一括 vs テーブル単位分離）

## ステータス

- [x] **決定**（2026-02-19更新: issue単位一括に変更）

## コンテキスト (課題と背景)

issue #27 + #31で7テーブル（User, Profile, OAuthAccount, Badge, Quest, QuestProgress, SkillTree）を実装する際、Alembicマイグレーションファイルをどの粒度で作成するか検討しました:

- **ロールバック戦略**: スキーマ変更を元に戻す際、どの単位で巻き戻すべきか
- **依存関係管理**: テーブル間の外部キー制約による依存順序を明確にする必要がある
- **保守性**: マイグレーションファイルが増えると管理コストが上がる
- **MVP優先**: ハッカソンでは最低限動くものを優先、過度な細分化は不要
- **マイグレーションの本質**: 環境同期が主目的、本番環境での部分的ロールバックは想定しない

## 決定 (Decision)

**issue単位で一括マイグレーション**する（1本のマイグレーションファイル）:

```
0001_create_all_tables.py
  - users（issue #27、skillsカラムなし）
  - profiles, oauth_accounts, badges, quests, quest_progress, skill_trees（issue #31）
```

### 実装原則

- **1 issue = 1マイグレーション**: issue単位で全テーブルをまとめる
- **all-or-nothing**: ロールバックはissue全体単位（部分的なロールバックは不要）
- **依存順序を内部で管理**: 1ファイル内でテーブル作成順序を制御
- **命名規則**: `000X_create_all_tables.py` で統一

## 代替案との比較 (Options)

### 1. テーブル単位分離（当初案、却下）

```python
# 0002_create_profiles_table.py
# 0003_create_oauth_accounts_table.py
# 0004_create_badges_table.py
# 0005_create_quests_table.py
# 0006_create_quest_progress_table.py
# 0007_create_skill_trees_table.py
```

- **Good**:
  - テーブル単位で巻き戻し可能（例: SkillTreeだけロールバック）
  - マイグレーション失敗時、どのテーブルで問題が起きたか特定しやすい
  - 依存関係が `down_revision` で明示される
- **Bad**:
  - **ハッカソンの現実に合わない**: 本番環境で部分的にロールバックするシナリオがない
  - **マイグレーションファイル数が多い**: 6-7本のファイル管理コスト
  - **依存関係が複雑**: テーブル単位で分離する必要性が薄い
  - **却下理由**: MVP優先のハッカソンでは過度な細分化、実用性が低い

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

- **シンプルさ**: 1ファイルで完結、管理が容易
- **MVP優先**: ハッカソンでは最低限動くものを優先、過度な細分化を回避
- **all-or-nothing**: issue単位でロールバック、部分的なロールバックの複雑さを排除
- **依存関係の内部管理**: 1ファイル内でテーブル作成順序を制御、外部依存なし
- **環境同期が主目的**: マイグレーションの本質（チームの環境統一）に集中

### Negative

- **部分的ロールバック不可**: issue全体をロールバックする必要がある
  - **対処法**: ハッカソンでは本番環境での部分ロールバックは想定しない
- **デバッグ時の特定が若干困難**: どのテーブルで失敗したか、ログから特定する必要がある
  - **対処法**: エラーログで十分特定可能、実害は小さい

### 実装ガイドライン

- **新規issue実装時**: 1 issue = 1マイグレーションファイルの原則を守る
- **カラム追加・変更時**: 別途マイグレーションファイルを作成（issue単位で分離）
- **ロールバック手順**: `alembic downgrade -1` でissue単位で巻き戻し
- **Phase 2以降**: 本番環境稼働後、部分的ロールバックが必要になったら機能単位グループ化を検討
