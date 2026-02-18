# ADR 003: CRUD実装パターン

## ステータス

- [x] **決定**

## コンテキスト (課題と背景)

PR #28 でUserモデルのCRUD操作を実装する際、以下の課題がありました:

- FastAPIのエンドポイントとSQLAlchemyの間をどのように分離するか
- Repository パターン vs シンプルなCRUD関数
- ビジネスロジック（Service層）をどこに配置するか
- ハッカソンのスピード感と将来の拡張性のバランス

## 決定 (Decision)

**シンプルなCRUD関数パターン**を採用する:

```python
# app/crud/user.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(username=user.username)
    db.add(db_user)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(db_user)
    return db_user
```

### 実装原則

- `crud/` ディレクトリに機能別ファイル（`user.py`, `quest.py` 等）を配置
- 関数は `Session` を第一引数で受け取る
- モデルを直接返却（Pydanticスキーマへの変換はAPI層で行う）
- トランザクション管理（commit/rollback）をCRUD関数内で完結
- 複雑なビジネスロジックが必要になったら `services/` 層を追加

## 代替案との比較 (Options)

### 1. Repository クラスパターン

```python
class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()
```

- **Good**: 
  - オブジェクト指向的でテストがしやすい（DIしやすい）
  - 複数のCRUD操作を1つのクラスにまとめられる
- **Bad**: 
  - ボイラープレートコードが増える（`__init__`等）
  - シンプルなCRUD操作には過剰設計
  - ハッカソンのスピード感に合わない
  - **却下理由**: MVP段階ではオーバーエンジニアリング

### 2. FastAPI Dependency としてRepositoryを注入

```python
def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

@app.get("/users/{user_id}")
def read_user(user_id: int, repo: UserRepository = Depends(get_user_repository)):
    return repo.get_by_id(user_id)
```

- **Good**: 
  - Dependency Injectionの利点を最大限活用
  - テストでモックに差し替えやすい
- **Bad**: 
  - 依存関係の階層が深くなりすぎる（`get_db` → `get_repository` → `endpoint`）
  - デバッグが複雑になる
  - **却下理由**: ハッカソン期間中のトラブルシューティングに時間がかかる

### 3. 全てAPI層に直接記述

```python
@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

- **Good**: 
  - 最速で実装できる
  - レイヤーが少なく、デバッグが容易
- **Bad**: 
  - テストが困難（エンドポイントをテストする必要がある）
  - コードの再利用ができない（例: 管理画面と通常画面で同じUserロジック）
  - 関心の分離ができていない（SRP違反）
  - **却下理由**: 将来の拡張性とテスタビリティが犠牲になる

## 結果 (Consequences)

### Positive

- **シンプル**: 関数ベースで理解しやすい、新メンバーのオンボーディングが容易
- **テスタビリティ**: 単体テストで `Session` をモックすれば簡単にテスト可能
- **再利用性**: エンドポイント以外（バッチ処理、管理画面等）でも利用可能
- **段階的拡張**: 複雑化したら `services/` 層を追加するだけ

### Negative

- **トランザクション境界が曖昧**: CRUD関数内でcommitするため、複数CRUD操作をまとめるトランザクションが難しい
  - **対処法**: 複雑な処理は `services/` 層を追加し、そこでトランザクション管理
- **ビジネスロジックの置き場所**: 単純なCRUD以上の処理をどこに書くか迷う可能性
  - **対処法**: 原則として `services/` 層を追加（例: `services/user.py`）
- **エラーハンドリング**: 各CRUD関数で try-except が重複する可能性
  - **対処法**: 共通のデコレーターやミドルウェアで対処（Future）

### 実装ガイドライン

- **MVP段階**: シンプルなCRUD関数で実装
- **Phase 2以降**: 以下の場合は `services/` 層を追加
  - 複数テーブルにまたがるトランザクション
  - 外部API呼び出しを含む処理
  - 複雑なビジネスロジック（ランク計算、バッジ付与等）
