# 010 スキルツリーAPI実装後のテスト戦略 - モック vs 統合テスト

## ステータス

- [x] **決定**

## コンテキスト (課題と背景)

### 実装内容（Issue #54）

スキルツリー生成API (`/api/v1/analyze/skill-tree`) を以下の機能で実装:

**`generate_skill_tree_ai()` の処理内容**:

1. **DBアクセス**: Profile/User取得、QuestProgress参照、SkillTreeテーブル更新
2. **GitHub API呼び出し**: リポジトリ分析、使用言語/技術スタック抽出、習得済みスキル推定
3. **LLM呼び出し**: Gemini APIでパーソナライズされたスキルツリー生成
4. **キャッシュ管理**: 7日間キャッシュ、generated_at判定
5. **強制上書き処理**: GitHub分析結果がLLM判定より優先（Step 6.5）

### 発生した課題

既存のAPIテスト (`test_analyze_mock.py`) が実装後に失敗:

### 発生した課題

既存のAPIテスト (`test_analyze_mock.py`) が実装後に失敗:

1. **DB依存**: `generate_skill_tree_ai()` はProfile/User/QuestProgress/SkillTreeテーブルへのアクセスが必須
   - TestClientはDBセッションをオーバーライドしていない
   - テストデータ（user_id=1のProfile/User）が存在しない
   - 結果: 6テストが500 Internal Server Errorで失敗

2. **外部API依存**: GitHub API呼び出しが発生（テスト実行時に実際のAPIコール不可）

3. **LLM依存**: Gemini API呼び出しが発生（高コスト、実行時間長い、レスポンス不安定）

### テスト修正の選択肢

テストファイル `test_analyze_mock.py` をどう扱うか:

- **A案**: DBセッションオーバーライド + テストデータ作成 → **完全な統合テスト**
- **B案**: `generate_skill_tree_ai()` をモック化 → **APIインターフェーステスト**
- **C案**: テストをスキップ → **検証なし**

### なぜA案（統合テスト）を採用しなかったか

**問題点**:

- `test_skill_tree_service.py` で既に統合テストを実施済み（12テスト）
  - LLM呼び出しのモック化テスト
  - GitHub API統合のモック化テスト
  - キャッシュ機能テスト
  - 強制上書き処理テスト（GitHub分析 > LLM判定）
  - DBアクセス・永続化テスト
- `test_analyze_mock.py` で同じテストを繰り返すと**重複**
- DBセッションオーバーライド、マイグレーション実行、テストデータ作成で**テストコード複雑化**

## 決定 (Decision)

**B案を採用**: `generate_skill_tree_ai()` をモック化して、**APIレイヤーのHTTPインターフェースのみ検証**

### 理由

1. **テスト役割の分離**:
   - `test_skill_tree_service.py`: **ビジネスロジック検証**（LLM/GitHub API/DB統合）← 既に12テスト実施済み
   - `test_analyze_mock.py`: **APIインターフェース検証**（HTTPステータス、レスポンススキーマ、FastAPIルーティング）← 今回修正

2. **テスト高速化**: DB/LLM/外部APIを使わないため、1秒未満で完了

3. **テスト独立性**: DB状態、外部API可用性に依存しない

4. **重複排除**: ビジネスロジックは別ファイルで検証済み、APIレイヤーに特化

### 「実装したのにモック化」の意図

**誤解を避けるための明確化**:

- ✅ **実装そのものは本番コード**（LLM + GitHub API + DB統合）
- ✅ **実装の詳細テストは `test_skill_tree_service.py` で実施済み**（12テスト）
- ✅ **`test_analyze_mock.py` はAPIレイヤーの薄いテスト**（HTTPインターフェース検証のみ）

**なぜモック化したか**:

- APIエンドポイント自体（FastAPIのルーティング、Pydanticスキーマ、HTTPステータスコード）の動作確認が目的
- ビジネスロジック（`generate_skill_tree_ai` の詳細）は別ファイルで検証済み
- **責務の分離**: APIレイヤーとビジネスロジック層を独立してテスト

### 実装内容

```python
with patch(
    "app.api.endpoints.analyze.generate_skill_tree_ai",
    new_callable=AsyncMock,
    return_value=mock_response,
):
    response = client.post("/api/v1/analyze/skill-tree", ...)
```

### 検証項目

1. **HTTPレスポンスコード**: 200 OK
2. **レスポンススキーマ**: `category`, `tree_data`, `generated_at` の存在
3. **tree_dataのJSON構造**: `nodes`, `edges`, `metadata` の構造検証
4. **全6カテゴリ対応**: parametrize で web/ai/security/infrastructure/design/game をテスト
5. **バリデーションエラー**: 無効な user_id, category, 必須フィールド欠如時の 422 エラー

### テスト役割分担

- `test_analyze_mock.py`: **APIエンドポイントのインターフェース検証**（レスポンス構造、HTTP仕様準拠）
- `test_skill_tree_service.py`: **AI実装のロジック検証**（LLM呼び出し、GitHub API統合、キャッシュ、強制上書き機能）

## 代替案との比較 (Options)

### 1. A案: DBセッションオーバーライド + テストデータ作成（完全な統合テスト）

- **Good**:
  - DB/LLM/GitHub APIを含めた完全なE2Eテスト
  - より現実に近い動作確認
- **Bad**:
  - **重複**: `test_skill_tree_service.py` で既に統合テスト実施済み（12テスト）
  - **複雑**: DBフィクスチャ、マイグレーション実行、外部APIモック化が必要
  - **低速**: DB初期化、LLMモックレスポンス生成で数秒かかる
  - **脆弱**: DB状態、マイグレーション変更で頻繁に壊れる

### 2. C案: テストをスキップ（検証なし）

- **Good**: シンプル、重複なし
- **Bad**:
  - **APIレイヤーの検証が失われる**
    - FastAPIのルーティング削除・変更を検知できない
    - Pydanticスキーマのフィールド追加・削除を検知できない
    - HTTPステータスコード変更（200→404等）を検知できない
  - **リグレッション検出不可**: エンドポイント仕様変更をCIで検知できない

### 3. 採用案: B案（モック化してAPIインターフェース検証）

- **Good**:
  - **責務の分離**: APIレイヤー（ルーティング、スキーマ、HTTP仕様）のみテスト
  - **高速**: DB/LLM/外部API不要、1秒未満で完了
  - **独立性**: DB状態に依存しない、CI/CDで安定動作
  - **重複排除**: ビジネスロジックは別ファイルでカバー済み
  - **明確な目的**: エンドポイント削除・スキーマ変更をCIで即座に検知
- **Bad**:
  - ビジネスロジックの詳細動作は検証されない
  - **⇒ 対策済み**: `test_skill_tree_service.py` で12テストカバー

## 影響範囲

- **変更ファイル**: `tests/test_api/test_analyze_mock.py`
- **テスト数**: 10テスト（スキルツリー6カテゴリ + バリデーション4件）
- **CI/CD**: 全テスト通過、Exit Code 0

## 補足

### テストカバレッジの詳細

#### `test_skill_tree_service.py` (12テスト) - ビジネスロジック検証

1. **キャッシュ機能**:
   - `test_generate_skill_tree_ai_cache_hit`: 7日以内のキャッシュを返却
   - `test_generate_skill_tree_ai_regenerate`: 10日前のキャッシュは再生成

2. **GitHub API統合**:
   - `test_generate_skill_tree_ai_with_github_data`: 使用言語からcompleted判定
   - `test_generate_skill_tree_ai_github_overrides_llm`: **GitHub分析がLLM判定を上書き（Step 6.5）**

3. **LLM呼び出し**:
   - `test_generate_skill_tree_ai_success`: 正常なJSON生成
   - `test_generate_skill_tree_ai_llm_failure_fallback`: LLM失敗時はベースラインJSON返却

4. **DB操作**:
   - Profile/User取得、SkillTreeテーブル更新、QuestProgress参照

5. **プロンプト生成**:
   - `test_build_skill_tree_prompt`: ユーザーランク、GitHub分析結果の埋め込み

#### `test_analyze_mock.py` (10テスト) - APIインターフェース検証

1. **HTTPレスポンス**: 200 OK、422 Unprocessable Entity
2. **レスポンススキーマ**: `category`, `tree_data`, `generated_at` の存在・型検証
3. **JSON構造**: `nodes`, `edges`, `metadata` の構造・フィールド検証
4. **全6カテゴリ対応**: web/ai/security/infrastructure/design/game のパラメトライズ
5. **バリデーション**: 無効なuser_id、category、必須フィールド欠如時のエラー

### なぜこの分割が適切か

**APIレイヤーとビジネスロジック層の責務分離**:

```
┌──────────────────────────────────────────┐
│ FastAPI Endpoint                         │
│ /api/v1/analyze/skill-tree              │  ← test_analyze_mock.py
│ - ルーティング                           │     (HTTPインターフェース)
│ - Pydanticスキーマ                       │
│ - HTTPステータスコード                   │
└──────────────┬───────────────────────────┘
               │ 呼び出し
               ▼
┌──────────────────────────────────────────┐
│ generate_skill_tree_ai()                 │
│ - DB: Profile/User/QuestProgress/SkillTree │ ← test_skill_tree_service.py
│ - GitHub API: リポジトリ分析              │     (ビジネスロジック)
│ - LLM: Gemini API                        │
│ - キャッシュ: 7日間判定                  │
│ - 強制上書き: GitHub > LLM (Step 6.5)   │
└──────────────────────────────────────────┘
```

**もしA案を採用した場合の問題**:

- `test_analyze_mock.py` でもDB/LLM/GitHub APIをモック化して統合テスト
- `test_skill_tree_service.py` と**完全に重複**
- 2つのファイルで同じロジックを二重にテスト
- どちらかが壊れたときに、どのレイヤーの問題か不明

- 新しいカテゴリ追加時: `SkillCategory` enumに追加すれば自動テスト
- レスポンススキーマ変更時: 即座にテスト失敗で検知可能
- ビジネスロジック変更時: `test_skill_tree_service.py` のみ修正すればよい

### テスト実行例

```bash
# APIインターフェース検証（高速・独立）
poetry run pytest tests/test_api/test_analyze_mock.py::TestSkillTreeGeneration -v
# 実行時間: < 1秒
# 依存: なし（モックのみ）
# 目的: FastAPIルーティング、Pydanticスキーマ、HTTPステータスコード検証

# ビジネスロジック検証（統合・詳細）
poetry run pytest tests/test_services/test_skill_tree_service.py -v
# 実行時間: 1〜3秒
# 依存: DB (SQLite in-memory)、LLM/GitHub APIモック
# 目的: キャッシュ、GitHub分析、LLM呼び出し、強制上書き処理の検証
```

### 具体例: エンドポイント削除を検知するシナリオ

**ケース1: エンドポイントを誤って削除**

```python
# analyze.py で誤って削除
# @router.post("/skill-tree", response_model=SkillTreeResponse)  ← コメントアウト
```

- `test_analyze_mock.py`: **即座に失敗** (404 Not Found)
- `test_skill_tree_service.py`: **通過**（関数自体は正常動作）
- ⇒ APIレイヤーの問題と特定可能

**ケース2: GitHub分析ロジックを誤って変更**

```python
# skill_tree_service.py で誤った判定
completion_signals = {}  # ← 常に空辞書を返す
```

- `test_analyze_mock.py`: **通過**（モック化されているため）
- `test_skill_tree_service.py`: **即座に失敗** (GitHub分析結果が反映されない)
- ⇒ ビジネスロジックの問題と特定可能

## 関連

- Issue #54: AI Phase 3 - スキルツリー生成（LLMパーソナライゼーション）
- Issue #35: モックAPIエンドポイント実装
- `test_skill_tree_service.py`: 12テストでAI実装の詳細検証
- `test_analyze_mock.py`: 10テストでAPIエンドポイント仕様検証
