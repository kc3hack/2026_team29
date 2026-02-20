# ADR 009: DB設計方針（正規化、型選択、外部キー戦略）

## ステータス

- [x] **決定**
- [x] **更新** (2026-02-19): JSON型 → JSONB型に変更（issue #45）

## コンテキスト (課題と背景)

issue #31で6テーブル（Profile, OAuthAccount, Badge, Quest, QuestProgress, SkillTree）を実装する際、プロジェクト全体のDB設計方針を明確にする必要がありました：

- **正規化の程度**: どこまで正規化するか（3NF？非正規化？）
- **型選択基準**: JSON vs JSONB、Enum vs 整数、Text vs String
- **外部キー制約**: どこまで外部キー制約を使うか、ON DELETE CASCADE の使用方針
- **インデックス戦略**: どのカラムにインデックスを張るか、UNIQUE制約の使い方
- **SQLite vs PostgreSQL**: 開発環境と本番環境の互換性をどう保つか
- **MVP優先**: ハッカソンでは最低限動くものを優先、過度な最適化は不要

## 決定 (Decision)

### 1. 正規化の程度: **第3正規形（3NF）を基本とする**

- **テーブル分割の基準**: 責務が異なるデータは別テーブルに分離
  - User（認証・ゲーミフィケーション） vs Profile（外部連携情報）
  - Quest（共有データ） vs QuestProgress（ユーザー固有データ）
- **非正規化の許容**: パフォーマンスのためのキャッシュカラムは許容
  - User.level, User.exp, User.rank はSkillTreeから算出可能だが、頻繁にアクセスするためキャッシュ

### 2. 型選択基準

#### JSON型 vs JSONB型（PostgreSQL）
- **基本方針**: ~~JSON型を使用（JSONB型は不要）~~ **→ JSONB型に変更（2026-02-19、issue #45）**
- **変更理由**:
  - **Langchain/フロントエンドとの統一的な操作**: JSONB型（バイナリ形式）で一貫した扱いが必要
  - **テスト環境の統一**: SQLite（BLOB型）/PostgreSQL（JSONB型）両対応
  - **スキルツリーのクリア状態更新・検索**: SkillTree.tree_data 内の各ノード（`completed` フラグ）をノード単位で更新・検索する予定があるため、JSONB の GIN インデックスによる JSON 内部検索（`@>`, `?` 演算子等）が必要になる（Issue #54 参照）
- **実装方針**:
  - PostgreSQL: JSONB型として保存
  - SQLite: BLOB型として保存（JSONBのバイナリ表現）
  - SQLAlchemyの`JSON().with_variant(JSONB, "postgresql")`で両DB対応
- **旧方針（参考）**:
  - ~~JSON型を使用（JSONB型は不要）~~
  - ~~理由: AI生成のツリー構造を全体として保存・取得するだけ、JSON内部の検索が不要~~

#### Enum vs 整数
- **基本方針**: Enumは文字列型、整数は数値演算が必要な場合
  - BadgeCategory, QuestCategory: Enum（文字列型）
  - Badge.tier: 整数（1-3: Bronze/Silver/Gold、数値演算は不要だが範囲バリデーションが簡単）
  - Quest.difficulty: 整数（0-9: ランクと同スケール、範囲検索が必要）

#### Text vs String
- **基本方針**: 長文はText型、短文はString型
  - Quest.description, Profile.portfolio_text: Text型（長文）
  - User.username, Profile.github_username: String型（短文、インデックス対象）

### 3. 外部キー制約: **すべてのFK関係に外部キー制約を使用**

- **ON DELETE CASCADE**: 使用しない（明示的な削除を推奨）
  - 理由: 意図しないデータ削除を防ぐ、監査ログが必要になる可能性
  - 例外: 将来的に親テーブル削除時に子テーブルも削除すべきケースが明確になったら検討

### 4. インデックス戦略

- **主キー**: すべてのテーブルに `id` カラム（自動インデックス）
- **外部キー**: すべてのFKカラムにインデックス（例: `user_id`, `quest_id`）
- **UNIQUE制約**: ビジネスロジック上一意であるべきカラムに付与
  - User.username: UNIQUE（認証用）
  - (user_id, provider): UNIQUE（OAuthAccount、同一プロバイダの重複防止）
  - (user_id, category): UNIQUE（SkillTree、カテゴリごとに1レコードのみ）

### 5. NULL許容とデフォルト値

- **基本方針**: 必須カラムは `nullable=False`、Optional は `nullable=True`
  - User.username, Quest.title: `nullable=False`
  - Profile.qiita_id, OAuthAccount.refresh_token: `nullable=True`
- **デフォルト値**: 初期値が明確な場合は設定
  - User.level: `default=1`
  - User.exp: `default=0`
  - SkillTree.tree_data: `default=lambda: {}`（空のJSON）

### 6. タイムスタンプ

- **created_at**: すべてのテーブルに付与（`server_default=func.now()`）
- **updated_at**: 更新が頻繁なテーブルに付与（`onupdate=func.now()`）
  - User, OAuthAccount: 更新が頻繁なため付与
  - Quest, Badge: 更新が少ないため不要（created_at のみ）
- **timezone**: すべて `DateTime(timezone=True)` でUTC管理

### 7. SQLite vs PostgreSQL 互換性

- **開発環境**: SQLite（Docker不要、軽量）
- **本番環境**: PostgreSQL（想定、ただしハッカソンではSQLiteのまま可能性もあり）
- **互換性の保ち方**:
  - JSON型を使用（どちらでも使える）
  - SQLAlchemy ORM でDB固有の機能を避ける
  - マイグレーションファイルで型を切り替える必要がある場合は、環境判定で分岐

## 代替案との比較 (Options)

### 1. 非正規化（すべてUserテーブルに統合）

- **Good**: JOIN不要、クエリがシンプル、パフォーマンス向上
- **Bad**:
  - テーブルが肥大化（Userに50カラム以上）
  - NULL許容カラムが増える（github_username, qiita_id等）
  - 責務が混在（認証、ゲーミフィケーション、外部連携）
  - **却下理由**: 保守性が低い、責務分離の原則に反する

### 2. JSONB型を優先（PostgreSQL）

- **Good**: JSON内部の検索が高速、GINインデックスで最適化可能
- **Bad（旧判断、2026-02-19に方針転換）**:
  - ~~MVP段階ではJSON内部検索が不要（全体を読むだけ）~~
  - ~~SQLiteとの互換性が低い（SQLiteはJSONB型をサポートしない）~~
  - 書き込みパフォーマンスが若干劣る
  - ~~**却下理由**: 現時点では過剰な最適化、互換性優先~~
- **方針転換（2026-02-19、issue #45）**:
  - Langchain/フロントエンドとの統一的な操作のため、JSONB型（BLOB型）を採用
  - SQLiteではBLOB型として保存することで互換性を確保

### 3. NoSQL（MongoDB等）

- **Good**: スキーマレス、JSON保存が得意、水平スケーリング容易
- **Bad**:
  - トランザクション管理が複雑
  - RDBMSの知見を活かせない
  - ハッカソンで新技術に挑戦するリスク
  - **却下理由**: MVP優先、既存の知見を活かす

### 4. ON DELETE CASCADE を使用

- **Good**: 親テーブル削除時に子テーブルも自動削除、コード量削減
- **Bad**:
  - 意図しないデータ削除のリスク
  - 監査ログが必要になった場合、削除履歴が残らない
  - デバッグが困難
  - **却下理由**: 安全性優先、明示的な削除を推奨

## 結果 (Consequences)

### Positive

- **責務分離**: テーブルごとに明確な責務、保守性向上
- **型安全性**: SQLAlchemy ORM + Pydantic で型チェックが効く
- **互換性**: SQLiteとPostgreSQLで共通のコードを使用可能
- **MVP優先**: 過度な最適化を避け、最低限動くものを優先
- **将来の拡張性**: 正規化により、新機能追加時のテーブル追加が容易

### Negative

- **JOIN の増加**: 正規化により、複数テーブルをJOINするクエリが増える
  - **対処法**: SQLAlchemy ORM の `relationship()` で簡潔に記述
- **パフォーマンス**: 非正規化より若干遅い
  - **対処法**: ハッカソン規模（数百ユーザー）では影響なし、将来的にインデックス最適化
- **JSONB型採用による書き込みコスト**: JSON型より書き込み時のパース処理が若干重い
  - **対処法**: ハッカソン規模では影響なし。スキルツリーはユーザー分析時のみ更新するため書き込み頻度が低い

### 実装ガイドライン

- **新規テーブル追加時**: 責務が異なる場合は別テーブルに分離
- **型選択時**: JSON内部検索が必要か検討し、不要ならJSON型を使用
- **外部キー**: すべてのFK関係に外部キー制約を付与、ON DELETE CASCADE は使用しない
- **インデックス**: 主キー、外部キー、UNIQUE制約のみ、過度なインデックスは避ける
- **Phase 2以降**: パフォーマンス問題が出てきたら、JSONB型への移行やインデックス最適化を検討
