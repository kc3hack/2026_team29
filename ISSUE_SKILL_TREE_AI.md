# Backend: AI実装Phase 3 - スキルツリー生成（LLMパーソナライゼーション）

## 目的

Issue #35で実装したモックAPIエンドポイント（`POST /api/v1/analyze/skill-tree`）を、LLM（Gemini）を使ったパーソナライズド実装に置き換える。ユーザーのGitHub活動、Qiita記事、学習履歴に基づいて、個別最適化されたスキルツリー（学習ロードマップ）を動的に生成する。

## 背景

- ✅ Issue #35: モック実装完了（全ユーザー共通の固定データを返却）
- ✅ Issue #36: ランク判定AI実装完了（LLM統合の基盤確立）
- ✅ Issue #31: SkillTreeモデル・CRUD実装完了（DB基盤）
- ⏳ 次のステップ: モック → AI実装への移行

現在のモック実装の制限事項:

- ユーザーの学習履歴を考慮しない
- GitHub/Qiitaの活動データを分析しない
- 全ユーザーに同じスキルツリーを返す

## 実装エンドポイント

### POST /api/v1/analyze/skill-tree - スキルツリー生成（AI実装）

**変更点**: `backend/app/services/mock_ai_service.py` の `generate_skill_tree_mock()` を削除し、新しい `skill_tree_service.py` に AI実装を追加。

**Request Body（変更なし）**:

```json
{
  "user_id": 1,
  "category": "web"
}
```

**Response（構造は同じ、内容が動的に生成される）**:

```json
{
  "category": "web",
  "tree_data": {
    "nodes": [
      {
        "id": "html-css",
        "name": "HTML/CSS基礎",
        "completed": true, // ← GitHub分析で動的に判定
        "description": "基本的なマークアップとスタイリング",
        "prerequisites": [],
        "estimated_hours": 20 // ← ユーザーのランクに応じて調整
      }
      // ... ユーザーに最適化されたスキル 5-10個
    ],
    "edges": [{ "from": "html-css", "to": "js-basics" }],
    "metadata": {
      "total_nodes": 8,
      "completed_nodes": 3, // ← GitHub分析結果
      "progress_percentage": 37.5,
      "next_recommended": ["react", "typescript"] // ← LLMが推奨
    }
  },
  "generated_at": "2026-02-20T12:00:00+09:00"
}
```

## アーキテクチャ

### ディレクトリ構造

```
backend/
├── app/
│   ├── api/endpoints/
│   │   └── analyze.py                    # 変更: DBセッション依存追加
│   ├── services/
│   │   ├── mock_ai_service.py            # 削除候補（or モック関数のみ削除）
│   │   ├── skill_tree_service.py         # 新規作成（AI実装）
│   │   └── github_service.py             # 新規作成（GitHub API統合）
│   ├── core/
│   │   └── prompts.py                    # 拡張: SKILL_TREE_ANALYSIS_TEMPLATE
│   └── crud/
│       └── skill_tree.py                 # 既存: get_skill_tree_by_user_category利用
├── data/
│   └── skill_trees/                      # 新規作成: JSONベースラインデータ
│       ├── README.md
│       ├── web.json
│       ├── ai.json
│       ├── security.json
│       ├── infrastructure.json
│       ├── design.json
│       └── game.json
└── tests/
    └── test_services/
        └── test_skill_tree_service.py    # 新規作成
```

### AI実装フロー

```
1. リクエスト受信 (user_id, category)
   ↓
2. 既存SkillTreeテーブル確認（キャッシュチェック）
   - generated_at が7日以内 → DBから返却（LLM呼び出しスキップ）
   - 古い or 存在しない → 次のステップへ
   ↓
3. ユーザー情報収集
   - Profileテーブル取得（github_username, qiita_id, rank）
   - GitHub API呼び出し（非同期）: 使用言語、リポジトリ分析
   - Qiita API呼び出し（非同期）: 記事タグ、専門分野
   - QuestProgressテーブル取得: 完了済み演習リスト
   ↓
4. ベースラインJSONロード
   - data/skill_trees/{category}.json 読み込み
   - LLMへのコンテキストとして使用
   ↓
5. LLM（Gemini）プロンプト生成
   - SKILL_TREE_ANALYSIS_TEMPLATE に情報埋め込み
   - GitHub分析結果でcompletedフラグ判定ロジックを指示
   - ランクに応じた学習時間調整を指示
   ↓
6. LLM呼び出し（temperature=0.3）
   - JSONレスポンス取得
   - パース＆バリデーション
   ↓
7. SkillTreeテーブル更新
   - tree_data, generated_at を更新
   - DB保存
   ↓
8. レスポンス返却
```

## 実装タスク

### 1. JSONベースラインデータ作成

**ファイル**: `backend/data/skill_trees/{category}.json`（全6カテゴリ）

- [ ] `web.json`: HTML/CSS → JavaScript → React/TypeScript → API設計
- [ ] `ai.json`: Python基礎 → NumPy/Pandas → 機械学習 → ディープラーニング → LLM
- [ ] `security.json`: ネットワーク基礎 → Webセキュリティ → 暗号化 → ペネトレーションテスト
- [ ] `infrastructure.json`: Linux基礎 → Docker → Kubernetes → CI/CD → IaC
- [ ] `design.json`: デザイン原則 → Figma → UXリサーチ → アクセシビリティ
- [ ] `game.json`: ゲーム数学 → Unity/Unreal Engine → ゲームAI

**JSON構造**（Issue #35のモックデータと互換性あり）:

```json
{
  "nodes": [...],
  "edges": [...],
  "metadata": {
    "total_nodes": 0,
    "completed_nodes": 0,
    "progress_percentage": 0.0,
    "next_recommended": []
  }
}
```

### 2. GitHub API統合

**ファイル**: `backend/app/services/github_service.py`

```python
async def analyze_github_profile(username: str) -> dict:
    """
    GitHub APIでユーザー分析

    Returns:
        {
            "languages": ["Python", "JavaScript", "TypeScript"],
            "repo_count": 42,
            "tech_stack": ["FastAPI", "React", "Docker"],
            "recent_activity": "過去30日で15コミット",
            "completion_signals": {
                "html-css": True,  # HTMLファイル存在
                "js-basics": True,  # .jsファイル存在
                "react": False,
                ...
            }
        }
    """
```

**実装要件**:

- 非同期HTTP呼び出し（`httpx.AsyncClient`）
- GitHub Personal Access Token（環境変数: `GITHUB_API_TOKEN`）
- Rate Limit考慮（キャッシュ戦略）
- リポジトリ言語分析（`/users/{username}/repos` エンドポイント）
- 技術スタック検出（package.json, pyproject.toml, Dockerfileなどの存在チェック）

**セキュリティ考慮**:

- トークンは `.env` で管理（ハードコード禁止）
- Rate Limitエラーハンドリング
- ユーザー名の存在チェック（404エラー処理）

### 3. Qiita API統合（オプショナル）

**ファイル**: `backend/app/services/qiita_service.py`

```python
async def analyze_qiita_profile(qiita_id: str) -> dict:
    """
    Qiita APIでユーザー分析

    Returns:
        {
            "tags": ["Python", "FastAPI", "機械学習"],
            "article_count": 12,
            "specialties": ["web", "ai"]
        }
    """
```

**注**: Qiita APIはオプション。時間的制約がある場合は後回し可。

### 4. LLMプロンプト拡張

**ファイル**: `backend/app/core/prompts.py`

```python
SKILL_TREE_ANALYSIS_TEMPLATE = """あなたは優秀なキャリアアドバイザーです。
このエンジニアの現在のスキルレベルと目標に基づいて、
パーソナライズされたスキルツリー（学習ロードマップ）を生成してください。

## エンジニア情報
- 現在のランク: {rank} ({rank_name})
- GitHub: {github_username}
  - 主な使用言語: {languages}
  - リポジトリ数: {repo_count}
  - 技術スタック: {tech_stack}
  - 最近の活動: {recent_activity}
- 習得済みスキル（GitHub分析結果）: {acquired_skills}
- 完了したQuest: {completed_quests}

## 選択されたカテゴリ: {category}

## ベースラインスキルツリー
{baseline_json}

## 生成要件
1. **未習得スキルの特定**: ベースラインから、ユーザーが次に学ぶべきスキル5-10個を選定
2. **completed判定**: GitHubリポジトリに該当技術があれば`completed: true`
3. **前提条件の定義**: スキル間の依存関係（prerequisites）を技術的に正確に
4. **難易度調整**: ユーザーのランクに応じた学習時間を推定
   - rank 0-2（初心者）: 基礎スキルを手厚く、長めの学習時間
   - rank 3-5（中級者）: 実践的スキル中心、標準的な学習時間
   - rank 6-9（上級者）: 先端技術・アーキテクチャスキル、短めの学習時間
5. **優先順位付け**: 次に取り組むべきスキル（next_recommended）を3つ提示

## 出力形式（JSON）
{{
  "nodes": [
    {{
      "id": "unique-skill-id",
      "name": "スキル名",
      "completed": true/false,
      "description": "スキルの説明",
      "prerequisites": ["前提スキルID"],
      "estimated_hours": 30
    }}
  ],
  "edges": [
    {{"from": "skill-a", "to": "skill-b"}}
  ],
  "metadata": {{
    "total_nodes": 8,
    "completed_nodes": 3,
    "progress_percentage": 37.5,
    "next_recommended": ["skill-x", "skill-y", "skill-z"]
  }}
}}

JSON以外の形式や追加の説明は含めず、JSONのみを出力してください。"""
```

### 5. スキルツリーサービス実装

**ファイル**: `backend/app/services/skill_tree_service.py`

```python
async def generate_skill_tree_ai(
    user_id: int,
    category: SkillCategory,
    db: Session
) -> SkillTreeResponse:
    """
    LLMを使用してパーソナライズされたスキルツリーを生成

    Steps:
    1. 既存SkillTreeテーブル確認（キャッシュ）
    2. なければ or 古ければ → 以下を実行
    3. Profileテーブルからユーザー情報取得
    4. GitHub/Qiita API非同期呼び出し
    5. QuestProgressテーブルから完了済みQuest取得
    6. ベースラインJSON読み込み
    7. LLMプロンプト生成
    8. Gemini呼び出し
    9. レスポンスパース＆SkillTreeテーブル更新
    10. レスポンス返却
    """
```

**キャッシュ戦略**:

- `generated_at`が**7日以内**であれば、DBから返却（LLM呼び出しスキップ）
- 7日以上前またはnullの場合は再生成

**エラーハンドリング**:

- GitHub API Rate Limit → デフォルト値でフォールバック
- JSON Parse Error → ベースラインJSONを返却
- Profile not found → 404エラー

### 6. エンドポイント変更

**ファイル**: `backend/app/api/endpoints/analyze.py`

```python
# 変更前
from app.services.mock_ai_service import generate_skill_tree_mock

@router.post("/skill-tree", response_model=SkillTreeResponse)
async def generate_skill_tree(request: SkillTreeRequest) -> SkillTreeResponse:
    result = generate_skill_tree_mock(...)
    return result

# 変更後
from app.services.skill_tree_service import generate_skill_tree_ai
from app.db.session import get_db

@router.post("/skill-tree", response_model=SkillTreeResponse)
async def generate_skill_tree(
    request: SkillTreeRequest,
    db: Session = Depends(get_db)
) -> SkillTreeResponse:
    result = await generate_skill_tree_ai(
        user_id=request.user_id,
        category=request.category,
        db=db
    )
    return result
```

### 7. テスト実装

**ファイル**: `backend/tests/test_services/test_skill_tree_service.py`

```python
class TestSkillTreeService:
    """スキルツリーAI実装のテスト"""

    def test_generate_skill_tree_ai_with_cache(self):
        """キャッシュが有効な場合はDBから返却"""

    def test_generate_skill_tree_ai_regenerate(self):
        """キャッシュが古い場合はLLM呼び出し"""

    def test_generate_skill_tree_ai_with_github_data(self):
        """GitHub分析結果がcompleted判定に反映される"""

    def test_generate_skill_tree_ai_rank_adjustment(self):
        """ランクに応じて学習時間が調整される"""

    @pytest.mark.integration
    async def test_generate_skill_tree_ai_full_flow(self):
        """実際のLLM呼び出しを含むフルフローテスト"""
```

**モック戦略**:

- GitHub API呼び出しは `unittest.mock.patch` でモック
- LLM呼び出しも基本的にモック（インテグレーションテストのみ実際に呼び出し）

## セキュリティ考慮

### 環境変数管理

```bash
# .env
GITHUB_API_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx  # GitHub Personal Access Token
QIITA_API_TOKEN=xxx  # Qiita APIトークン（オプション）
```

**セキュリティチェックリスト**:

- [ ] `.env` ファイルを `.gitignore` に追加済みか
- [ ] トークンのハードコードは一切ないか
- [ ] GitHub API Rate Limit対策は実装されているか
- [ ] user_id存在チェック（Profileテーブル参照）
- [ ] LLMへの機密情報送信防止（portfolio_textのサニタイズ）

### Input Validation

- [ ] user_id: 正の整数（gt=0）
- [ ] category: SkillCategory Enum（6種類のみ許可）
- [ ] GitHub username: 存在チェック（404エラー処理）

## テスト要件

### 単体テスト

- [ ] ベースラインJSON読み込み成功
- [ ] キャッシュロジック（7日以内/以降）
- [ ] GitHub API分析結果のパース
- [ ] LLMレスポンスのJSON解析
- [ ] エラーハンドリング（GitHub API失敗、JSON Parse失敗）

### インテグレーションテスト

- [ ] 実際のGitHub API呼び出し（テストユーザーで）
- [ ] 実際のLLM呼び出し（Gemini）
- [ ] SkillTreeテーブル更新の確認
- [ ] キャッシュ機能の検証

### テストカバレッジ目標

- `skill_tree_service.py`: **80%以上**
- `github_service.py`: **70%以上**

## 完了条件（DoD）

- [ ] 全6カテゴリのベースラインJSON作成完了
- [ ] GitHub API統合完了（言語分析、completed判定）
- [ ] LLMプロンプト実装完了（SKILL_TREE_ANALYSIS_TEMPLATE）
- [ ] skill_tree_service.py実装完了
- [ ] エンドポイント変更完了（DBセッション依存追加）
- [ ] キャッシュロジック実装完了（7日間）
- [ ] テスト10件以上、全パス
- [ ] インテグレーションテスト実施（実際のLLM呼び出し）
- [ ] Swagger UIで動作確認（スクリーンショット撮影）
- [ ] 環境変数（GITHUB_API_TOKEN）のドキュメント化
- [ ] Issue #35のモック実装を削除 or 無効化

## 依存

- ✅ Issue #31: SkillTreeモデル・CRUD実装（PR #42マージ済み）
- ✅ Issue #35: モックAPIエンドポイント（現在実装中）
- ✅ Issue #36: AI基盤（LangChain + LLM統合）マージ済み

## 次のステップ（Phase 4）

- Issue #XX: AI実装Phase 4 - 演習生成（RAG統合）
- Issue #XX: GitHub OAuth認証（より詳細な分析）
- Issue #XX: スキルツリーの自動更新（週次バッチ処理）

## 参考

- Issue #35: モックAPIエンドポイント実装
- Issue #36: ランク判定AI実装（LLM統合パターン参考）
- [backend/app/services/rank_service.py](../../backend/app/services/rank_service.py): LLM呼び出しパターンの参考実装
- [GitHub REST API Documentation](https://docs.github.com/en/rest)
- [Qiita API v2 Documentation](https://qiita.com/api/v2/docs)
