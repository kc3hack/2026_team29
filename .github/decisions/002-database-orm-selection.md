# ADR 002: DB接続基盤とORM選定

## ステータス

- [x] **決定**

## コンテキスト (課題と背景)

PR #24, #28 でバックエンドのDB接続基盤を構築する際、以下の要件がありました:

- ハッカソンのため、短期間でDBスキーマ変更が頻繁に発生する
- Pythonエコシステムでのデファクトスタンダードを採用したい
- SQLインジェクション対策など、セキュリティを担保したい
- チームメンバーのSQL習熟度にバラつきがある
- 開発環境ではSQLiteを使用し、本番ではPostgreSQLに切り替える可能性がある

## 決定 (Decision)

以下の技術スタックを採用する:

1. **ORM**: SQLAlchemy 2.0系
2. **マイグレーションツール**: Alembic
3. **セッション管理**: FastAPIのDependency Injection (`get_db`)
4. **開発DB**: SQLite (file-based)

### 実装パターン

```python
# Session管理
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
```

## 代替案との比較 (Options)

### 1. Raw SQL (SQL直書き)

- **Good**: 
  - パフォーマンス最速
  - SQLに精通していれば学習コストなし
- **Bad**: 
  - SQLインジェクションリスクが高い（プレースホルダ忘れのリスク）
  - スキーマ変更時の修正漏れが発生しやすい
  - 型安全性がない（Pydanticとの整合性チェックが困難）
  - **却下理由**: ハッカソンのスピード感では、セキュリティリスクが高すぎる

### 2. SQLModel (Pydantic + SQLAlchemy統合)

- **Good**: 
  - FastAPIとの相性が良い（PydanticベースのORM）
  - スキーマとモデルの二重管理が不要
- **Bad**: 
  - まだ新しく、Stack Overflowなどの情報が少ない
  - 複雑なクエリでハマった時に時間が溶けるリスク
  - **却下理由**: ハッカソン期間中のトラブルシューティングリスクが高い

### 3. Peewee (軽量ORM)

- **Good**: 
  - シンプルで学習コストが低い
  - ドキュメントが分かりやすい
- **Bad**: 
  - コミュニティがSQLAlchemyより小さい
  - FastAPIエコシステムとの統合例が少ない
  - **却下理由**: 将来の拡張性とエコシステムの豊富さでSQLAlchemyが優位

## 結果 (Consequences)

### Positive

- **セキュリティ**: ORMによりSQLインジェクションのリスクが大幅に低減
- **型安全性**: SQLAlchemy 2.0のType Hints対応により、IDEの補完が効く
- **マイグレーション**: Alembicによりスキーマ変更履歴が管理され、ロールバックも容易
- **エコシステム**: FastAPIとの統合例が豊富で、トラブルシューティングが容易
- **DB切り替え**: SQLiteからPostgreSQLへの移行がconnection stringの変更のみで可能

### Negative

- **学習コスト**: SQLAlchemyの概念（Session, Query, Relationship等）を理解する必要がある
- **パフォーマンス**: Raw SQLと比較すると、若干のオーバーヘッドが発生
- **N+1問題**: 不適切な実装でパフォーマンス問題が発生する可能性（Future: `joinedload`等で対処）
- **初期設定**: Alembicの初期設定（alembic.ini, env.py）に時間がかかる

### 実装時の注意点

- `autocommit=False, autoflush=False` でトランザクション制御を明示的に行う
- SQLite使用時は `check_same_thread=False` を設定
- `get_db` 内でエラーハンドリングと `db.rollback()` を実装
