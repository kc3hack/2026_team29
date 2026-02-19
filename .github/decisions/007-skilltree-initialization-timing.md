# ADR 007: SkillTree初期化タイミング（ユーザー作成時 vs 遅延初期化）

## ステータス

- [x] **決定**

## コンテキスト (課題と背景)

issue #31でSkillTreeテーブル（6カテゴリ: WEB, AI, SECURITY, INFRASTRUCTURE, DESIGN, GAME）を実装する際、以下の課題がありました:

- **仕様要件**: product-specでは「ユーザー作成時に6カテゴリのSkillTreeを自動生成」と定義
- **LangChain連携**: AIエージェントがツールでSkillTreeを参照・更新する際、未初期化だと処理が複雑化
- **オーバーヘッド**: 遅延初期化（初回アクセス時）だと、LangChainツール呼び出しのたびに初期化チェックが必要
- **トランザクション境界**: UserとSkillTreeは密接に関係しており、同一トランザクション内で管理すべき
- **ADR 003準拠**: トランザクション管理はCRUD関数内で完結する方針

## 決定 (Decision)

**ユーザー作成時に自動初期化（CRUD層で実装）**を採用する:

```python
# app/crud/user.py
def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(username=user.username)
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        # ユーザー作成時に6カテゴリのSkillTreeを自動初期化
        initialize_skill_trees_for_user(db, db_user.id)
    except Exception:
        db.rollback()
        raise
    return db_user
```

### 実装原則

- **初期化タイミング**: `create_user()` 内で `initialize_skill_trees_for_user()` を呼び出し
- **トランザクション**: User作成とSkillTree初期化を同一トランザクション内で実行（ADR 003準拠）
- **失敗時のロールバック**: SkillTree初期化失敗時はUser作成もロールバック
- **密結合の許容**: UserとSkillTreeは密接に関係しているため、CRUD層での結合を許容

## 代替案との比較 (Options)

### 1. 遅延初期化（初回アクセス時に自動生成）

```python
def get_skill_tree_by_user_category(db: Session, user_id: int, category: SkillCategory):
    tree = db.query(SkillTree).filter(...).first()
    if tree is None:
        # 初回アクセス時に自動生成
        tree = SkillTree(user_id=user_id, category=category.value, tree_data={})
        db.add(tree)
        db.commit()
    return tree
```

- **Good**:
  - ユーザー作成時の処理が軽量（SkillTree初期化が不要）
  - 使われないカテゴリは初期化されない（DB容量削減）
- **Bad**:
  - LangChainツール呼び出しのたびに「未初期化チェック → 初期化」が必要
  - 初回アクセス時のオーバーヘッド（LLM応答が遅延）
  - product-specの「ユーザー作成時に6カテゴリ自動生成」要件に反する
  - **却下理由**: LangChain連携時のオーバーヘッドが大きい、仕様違反

### 2. 手動初期化（管理APIで実行）

- **Good**: 初期化タイミングを管理者が制御可能
- **Bad**:
  - ユーザー登録のたびに管理者が手動実行する必要がある
  - 初期化忘れのリスク（運用ミス）
  - ユーザー体験が悪い（SkillTreeが表示されない）
  - **却下理由**: 運用コストが高い、比較にすらならない

### 3. バッチ初期化（CRON jobで定期実行）

- **Good**: ユーザー作成時の処理が軽量、まとめて初期化で効率的
- **Bad**:
  - CRON実行までの時間、SkillTreeが存在しない（ユーザー体験が悪い）
  - CRON未実行時（サーバー停止等）に初期化されないリスク
  - 呼び出しタイミングが固定だが、存在しない時間に操作すると壊れる
  - **却下理由**: ユーザー体験が悪い、タイミング制御が困難

## 結果 (Consequences)

### Positive

- **オーバーヘッド削減**: LangChainツール呼び出し時に初期化チェック不要
- **仕様準拠**: product-specの「ユーザー作成時に6カテゴリ自動生成」要件を満たす
- **ユーザー体験**: ユーザー登録直後からSkillTreeが利用可能
- **トランザクションのアトミック性**: User作成失敗時はSkillTreeも作成されない（ADR 003準拠）
- **ADR 003との整合性**: トランザクション管理をCRUD関数内で完結

### Negative

- **ユーザー作成時の処理時間**: 6カテゴリ分のINSERT（約10-20ms増加）
  - **対処法**: ハッカソン規模（数百ユーザー）では影響なし
- **密結合**: `create_user()` がUserとSkillTreeの2つのテーブルに依存
  - **対処法**: UserとSkillTreeは仕様上密接に関係しており、許容範囲内

### 実装ガイドライン

- **MVP段階**: CRUD層（`create_user()`）で直接 `initialize_skill_trees_for_user()` を呼び出し
- **トランザクション管理**: ADR 003に従い、CRUD関数内でcommit/rollbackを完結
- **失敗時の挙動**: User作成もロールバックされる（all-or-nothing）
