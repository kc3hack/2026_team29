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
4. **キャッシュ管理**: 10分間キャッシュ、generated_at判定（ハッカソン最適化）
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
│ - キャッシュ: 10分間判定                 │
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

---

## 後続の決定: キャッシュ期間の変更（ハッカソン用最適化）

### 背景

初期実装では CACHE_VALID_DAYS = 7（7日間）でスキルツリーをキャッシュしていたが、以下の問題が判明:

**ハッカソン環境における課題**:

1. **デモ再現性の欠如**:
   - 2日間のハッカソン期間中、ユーザーがGitHubで新しいコミット/リポジトリを作成してもスキルツリーが更新されない
   - 審査員や来場者にAI機能を実演する際、「GitHubと連携している」ことを証明できない

2. **GitHub分析の優先度矛盾**:
   - Step 6.5で「GitHub分析結果 > LLM判定」という強制上書き機能を実装したが、7日間キャッシュではGitHub APIを呼ばない
   - 最も重要な「ユーザーの実際のスキル」を反映する機能が動作しない

3. **LLMコスト最適化の誤解**:
   - 本番環境ではGemini APIコスト削減のため長期キャッシュが有効
   - **しかしハッカソンでは機能デモが最優先**、コストは二の次

### 決定

**CACHE_VALID_MINUTES = 10**（10分間）に変更

**根拠**:

- **デモ体験**:
  - 来場者がGitHubでクイックコミット → 10分後に再生成 → 「習得済み」スキルが増えることを確認可能
  - LLM+GitHub統合の価値を実演できる

- **負荷対策**:
  - 10分間は連打防止として機能（Rate Limit保護）
  - ハッカソン期間中の想定トラフィック（数十人×数回/日）では十分

- **GitHub API Rate Limit**:
  - 未認証: 60req/h → 1分で1回まで ⇒ 10分キャッシュで安全マージン確保
  - 認証済み: 5000req/h → 余裕あり

### 実装

**変更箇所**:

```python
# backend/app/services/skill_tree_service.py
CACHE_VALID_MINUTES = 10  # 旧: CACHE_VALID_DAYS = 7

def _is_cache_valid(generated_at: datetime | None) -> bool:
    return (now - generated_at) < timedelta(minutes=CACHE_VALID_MINUTES)
```

**環境変数化**:

```dotenv
# backend/.env.example
# SKILL_TREE_CACHE_MINUTES=10  # 将来的に本番環境で調整可能（現在は未実装）
```

⇒ ハッカソン後、本番デプロイ時に環境変数で制御できるよう拡張可能

### トレードオフ

**メリット**:

- ✅ リアルタイムでGitHub分析を反映（デモ効果大）
- ✅ LLMパーソナライゼーションの価値を実証可能
- ✅ ユーザーフィードバックを即座に取得できる

**デメリット**:

- ⚠️ Gemini APIコール回数増加（初回生成後10分で再度LLM呼び出し可能）
- ⚠️ 本番環境では不適切（数時間〜1日が推奨）

**リスク軽減策**:

- ハッカソン終了時に`.env`でキャッシュ期間を延長する手順をREADME化
- ADR 010に「本番では環境変数で制御すべき」と明記

### 影響範囲

**テストコード**:

- `test_skill_tree_service.py`: キャッシュ判定ロジックのテストは引き続き動作（`CACHE_VALID_MINUTES`参照）
- `test_analyze_mock.py`: モック化されているため影響なし

**デプロイ**:

- Docker環境変数でオーバーライド可能（将来対応）
- 現状はソースコード固定値（ハッカソン期間中のみ）

### 今後の方針

**本番化時のアクション**:

1. `settings.py`に `SKILL_TREE_CACHE_MINUTES` 環境変数を追加
2. デフォルト値を `1440`（1日）に設定
3. `skill_tree_service.py`で `settings.SKILL_TREE_CACHE_MINUTES` 参照に変更
4. `.env.example`の設定項目をアンコメント

**備考**:

- ハッカソン期間中は固定値10分で運用
- プロダクション環境では必ず環境変数化すること

---

## 機能要件チェックリスト - Issue #54

### ✅ 実装完了項目

| 機能                             | 実装状況 | 検証方法                                                         |
| -------------------------------- | -------- | ---------------------------------------------------------------- |
| **LLM統合**                      | ✅       | `test_generate_skill_tree_ai_regenerate` (line 71)               |
| **GitHub API統合**               | ✅       | `test_generate_skill_tree_ai_with_github_data` (line 158)        |
| **GitHub優先上書き（Step 6.5）** | ✅       | `test_generate_skill_tree_ai_github_overrides_llm` (line 231)    |
| **10分間キャッシュ**             | ✅       | `test_generate_skill_tree_ai_with_cache` (line 28)               |
| **6カテゴリ対応**                | ✅       | `test_load_baseline_json_all_categories` (line 398)              |
| **User不在時404エラー**          | ✅       | `test_generate_skill_tree_ai_user_not_found` (line 345)          |
| **LLM失敗時フォールバック**      | ✅       | `test_generate_skill_tree_ai_llm_failure_fallback` (line 358)    |
| **HTTPエンドポイント**           | ✅       | `test_generate_skill_tree_all_categories` (test_analyze_mock.py) |

### 📊 手動テスト実行手順

```bash
# 1. テストユーザー作成
cd backend
poetry run python scripts/seed_test_data.py

# 2. スキルツリー生成（user_id=1, category=web）
curl -X POST http://localhost:8000/api/v1/analyze/skill-tree \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "category": "web"}' | jq

# 期待結果:
# - HTTPステータス: 200 OK
# - category: "web"
# - tree_data.nodes: 20個のノード（id, name, completed, description, prerequisites, estimated_hours）
# - tree_data.edges: 22個のエッジ（from, to）
# - tree_data.metadata: total_nodes, completed_nodes, progress_percentage, next_recommended
# - generated_at: ISO8601形式のタイムスタンプ
```

### 🎯 機能要件の動作確認ポイント

1. **LLMパーソナライゼーション**:
   - ユーザーのrank（2, 5, 8）によって説明文が変化
   - GitHub分析結果（使用言語、技術スタック）がプロンプトに反映

2. **GitHub分析優先**:
   - `github_username` に実在するアカウント（例: Inlet-back）を指定
   - `completed: true` となるノードがGitHub分析結果と一致
   - LLMが `false` と判定してもGitHub分析が `true` なら上書き

3. **キャッシュ動作**:
   - 初回: LLM呼び出し（数秒かかる）
   - 10分以内の再実行: キャッシュから即座に返却（< 100ms）
   - 10分経過後: 自動再生成

4. **エラーハンドリング**:
   - 存在しないuser_id → `{"detail": "User X not found"}` (404)
   - 無効なcategory → `422 Unprocessable Entity`
   - LLM API失敗 → ベースラインJSONを返却（縮退運転）

### 📝 自動テスト一覧

**サービス層** (`test_skill_tree_service.py`):

- ✅ `test_generate_skill_tree_ai_with_cache` - キャッシュ有効時はDB返却
- ✅ `test_generate_skill_tree_ai_regenerate` - キャッシュ期限切れでLLM再生成
- ✅ `test_generate_skill_tree_ai_with_github_data` - GitHub分析結果反映
- ✅ `test_generate_skill_tree_ai_github_overrides_llm` - GitHub優先上書き（Step 6.5）
- ✅ `test_generate_skill_tree_ai_user_not_found` - User不在で404
- ✅ `test_generate_skill_tree_ai_llm_failure_fallback` - LLM失敗でベースライン返却
- ✅ `test_is_cache_valid_within_7_days` - キャッシュ期間判定（10分以内）
- ✅ `test_is_cache_valid_over_7_days` - キャッシュ期間判定（10分経過）
- ✅ `test_load_baseline_json_success` - ベースラインJSON読み込み
- ✅ `test_load_baseline_json_all_categories` - 全6カテゴリ読み込み
- ✅ `test_build_skill_tree_prompt` - LLMプロンプト生成

**API層** (`test_analyze_mock.py`):

- ✅ `test_generate_skill_tree_all_categories` - 全6カテゴリHTTPエンドポイント
- ✅ `test_generate_skill_tree_structure` - tree_data構造検証
- ✅ `test_generate_skill_tree_validation_error` - バリデーションエラー処理

**実行コマンド**:

```bash
# 全テスト実行（22テスト、実行時間: 2-3秒）
poetry run pytest tests/test_services/test_skill_tree_service.py tests/test_api/test_analyze_mock.py -v

# 簡潔な出力
poetry run pytest tests/test_services/test_skill_tree_service.py tests/test_api/test_analyze_mock.py -q
```
