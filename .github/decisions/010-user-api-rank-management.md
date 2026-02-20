# ADR 010: User API設計 - rankフィールドの管理方針

## ステータス

- [x] **決定**

## コンテキスト (課題と背景)

Issue #51 で `PUT /users/{user_id}` エンドポイントを実装する際、`rank` フィールドの扱いについて以下の問題が判明した。

### 問題1: PUT /users/{id} に rank を公開するとユーザーが改ざん可能

`PUT /users/{id}` に `rank` フィールドを含めた場合、任意のユーザーが `rank=9`（世界樹）を自由にセットできる。AI分析を経ずにランクを操作できることになり、ゲームバランスを破壊する。

### 問題2: rankとexpの整合性バリデータとMVPフローの矛盾

`app/schemas/user.py` の `User` レスポンススキーマに以下のバリデータが存在していた:

```python
@model_validator(mode="after")
def validate_rank_consistency(self) -> "User":
    expected_rank = calculate_rank(self.exp)
    if self.rank != expected_rank:
        raise ValueError(...)
```

product-spec のMVPフローでは、AIが `rank=4` と判定した状態で `exp=0` のままになるため、このバリデータは **500エラー** を引き起こす。

product-spec 4.2:
> **MVP段階**: 初回分析時のランク決定のみ実装。
> **Future**: ポイント制や特定条件達成によるランクアップ機能。

MVPではrankはAIが直接決定し、expの蓄積によるrankupはFutureスコープ。

### rankとexpの関係

`rank = calculate_rank(exp)` という関係性は定義されているが（`RANK_THRESHOLDS`）、それはFutureのexp蓄積ランクアップのための設計。MVPではrankはAI判定で決まり、expとの連動はない。

また、rankが更新されるとスキルツリーの再生成フローが走る可能性もある（Issue #54）。このような複合的な処理はHTTPエンドポイントから直接操作できるべきではなく、サービス層・CRUD層で制御すべき。

## 決定 (Decision)

### 1. `PUT /users/{user_id}` から `rank` を除外

```python
class UserUpdate(BaseModel):
    username: str | None = None
    # rank / level / exp はサーバー側で管理するため含めない
```

### 2. AI専用のCRUD関数 `update_user_rank` を追加

AI サービス（LangChain / rank_service.py）からのみ呼び出される内部関数として `app/crud/user.py` に実装。HTTPエンドポイントには公開しない。

```python
def update_user_rank(db: Session, user_id: int, rank: int) -> User | None:
    """AI分析結果のランク保存専用。エンドポイントには公開しない。"""
```

### 3. `validate_rank_consistency` バリデータを削除

MVPではrankとexpの連動はFutureスコープ。バリデータはFutureのランクアップ実装時に改めて検討する。

### rankの更新フロー（MVP）

```
POST /analyze/rank (github_username, ...)
  └─ analyze_user_rank() が LLM でpercentile・rank を判定して結果を返す
  └─ フロントはレスポンス（rank, rank_name, reasoning）を表示するだけ
  └─ ※ DB への rank 保存は Future スコープ（Issue #54 等で実装予定）

PUT /users/{id} では rank は変更不可
```

> **Note**: 現在の `analyze_user_rank()`（`app/services/rank_service.py`）は `db` / `user_id` を受け取らず、LLM 判定結果を返すだけの純粋な分析ツールとして実装している。`update_user_rank(db, user_id, rank)` の呼び出しは AI サービス統合（Issue #54）のタイミングで追加する。

### rankの更新フロー（Future: Issue #54 実装時）

**設計原則**: rank の UPDATE はエンドポイントがサーバー内部で完結させる。フロントエンドは analyze 結果を受け取るだけでよく、別途 `PUT /users/{id}` で保存する必要はない。Issue #54 の `generate_skill_tree_ai(user_id, category, db)` が SkillTree テーブルを直接更新するパターンと同じ。

```
POST /analyze/rank (user_id, github_username, ...)
  └─ analyze_user_rank(db, user_id, ...) を呼び出し
  └─ LLM が percentile から rank 判定
  └─ 内部で update_user_rank(db, user_id, rank) を呼び出して DB 保存
  └─ フロントはレスポンスを表示するだけ（DB 保存はサーバー側で完結）

PUT /users/{id} では rank は変更不可（変わらず）
```

## 代替案との比較 (Options)

### 1. PUT /users/{id} に rank を含め、フロントが保存する

- **Good**: シンプル、実装が容易
- **Bad**: ユーザーが rank を自由に改ざん可能。MVP段階でOAuth認証が未実装のため、現時点で安全に実装できない
- **却下理由**: セキュリティリスク

### 2. POST /users/{id}/rank-init 専用エンドポイントを追加

- **Good**: 意図が明確
- **Bad**: エンドポイントが増えてAPIが複雑になる。AI内部でCRUD関数を呼べば同じことが実現できる
- **却下理由**: 不要な複雑性の追加（YAGNI）

## 結果 (Consequences)

### Positive

- **セキュリティ**: ユーザーによるrank改ざんが不可能
- **MVP優先**: 技術負債を増やさず、動くものを優先して提供
- **拡張性**: Future（ランクアップ・スキルツリー再生成連携）実装時は `update_user_rank` を拡張するだけでよい

### Negative

- **validate_rank_consistency の削除**: バリデータによる自動チェックがなくなる
  - **対処法**: `update_user_rank` を内部専用CRUDに限定し、rank変更経路を制御する
- **expとrankの非連動（MVP）**: expが増えてもrankは変わらない
  - **対処法**: Future実装時（Issue #XX）に連動ロジックを追加する

## 関連

- Issue #51: User API エンドポイント実装
- Issue #54: AI実装Phase 3 - スキルツリー生成（`update_user_rank` の利用元候補）
- ADR 005: APEX Legendsスタイルランク分布（rankの意味・定義）
- product-spec 4.2: ランクアップ方針（MVP vs Future）

## 変更履歴

- 2026-02-20: 決定（Issue #51 設計議論）
