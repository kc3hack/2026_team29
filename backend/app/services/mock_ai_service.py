"""
モックAIサービス - Issue #35

Phase 2: フロントエンド開発と並行作業可能な固定レスポンス返却
Phase 3: 実際のAI実装（LLM統合）に置き換え予定
"""

from datetime import datetime, timezone

from app.models.enums import QuestCategory, SkillCategory
from app.schemas.analyze import (
    QuestGenerationResponse,
    QuestResource,
    SkillTreeResponse,
)


# ====================================
# スキルツリー生成（モック）
# ====================================

# カテゴリ別スキルツリーデータ（全6種類）
MOCK_SKILL_TREES = {
    SkillCategory.WEB: {
        "nodes": [
            {
                "id": "html-css",
                "name": "HTML/CSS基礎",
                "completed": True,
                "description": "基本的なマークアップとスタイリング",
                "prerequisites": [],
                "estimated_hours": 20,
            },
            {
                "id": "js-basics",
                "name": "JavaScript基礎",
                "completed": True,
                "description": "変数、関数、DOM操作の基礎",
                "prerequisites": ["html-css"],
                "estimated_hours": 30,
            },
            {
                "id": "react",
                "name": "React/Next.js",
                "completed": False,
                "description": "モダンフロントエンドフレームワーク",
                "prerequisites": ["js-basics"],
                "estimated_hours": 50,
            },
            {
                "id": "typescript",
                "name": "TypeScript",
                "completed": False,
                "description": "型安全なJavaScript開発",
                "prerequisites": ["js-basics"],
                "estimated_hours": 40,
            },
            {
                "id": "api-design",
                "name": "REST API設計",
                "completed": False,
                "description": "API設計とOpenAPI仕様",
                "prerequisites": ["js-basics"],
                "estimated_hours": 30,
            },
        ],
        "edges": [
            {"from": "html-css", "to": "js-basics"},
            {"from": "js-basics", "to": "react"},
            {"from": "js-basics", "to": "typescript"},
            {"from": "js-basics", "to": "api-design"},
        ],
        "metadata": {
            "total_nodes": 5,
            "completed_nodes": 2,
            "progress_percentage": 40.0,
            "next_recommended": ["react", "typescript"],
        },
    },
    SkillCategory.AI: {
        "nodes": [
            {
                "id": "python-basics",
                "name": "Python基礎",
                "completed": True,
                "description": "Python文法とデータ構造",
                "prerequisites": [],
                "estimated_hours": 25,
            },
            {
                "id": "numpy-pandas",
                "name": "NumPy/Pandas",
                "completed": True,
                "description": "データ処理と数値計算ライブラリ",
                "prerequisites": ["python-basics"],
                "estimated_hours": 30,
            },
            {
                "id": "machine-learning",
                "name": "機械学習基礎",
                "completed": False,
                "description": "scikit-learnを使った機械学習",
                "prerequisites": ["numpy-pandas"],
                "estimated_hours": 60,
            },
            {
                "id": "deep-learning",
                "name": "ディープラーニング",
                "completed": False,
                "description": "PyTorch/TensorFlowによるニューラルネット",
                "prerequisites": ["machine-learning"],
                "estimated_hours": 80,
            },
            {
                "id": "llm-application",
                "name": "LLMアプリケーション",
                "completed": False,
                "description": "LangChainとRAGシステム構築",
                "prerequisites": ["deep-learning"],
                "estimated_hours": 50,
            },
        ],
        "edges": [
            {"from": "python-basics", "to": "numpy-pandas"},
            {"from": "numpy-pandas", "to": "machine-learning"},
            {"from": "machine-learning", "to": "deep-learning"},
            {"from": "deep-learning", "to": "llm-application"},
        ],
        "metadata": {
            "total_nodes": 5,
            "completed_nodes": 2,
            "progress_percentage": 40.0,
            "next_recommended": ["machine-learning"],
        },
    },
    SkillCategory.SECURITY: {
        "nodes": [
            {
                "id": "network-basics",
                "name": "ネットワーク基礎",
                "completed": True,
                "description": "TCP/IP、HTTP、DNS",
                "prerequisites": [],
                "estimated_hours": 30,
            },
            {
                "id": "web-security",
                "name": "Webセキュリティ",
                "completed": False,
                "description": "XSS、SQLi、CSRF対策",
                "prerequisites": ["network-basics"],
                "estimated_hours": 40,
            },
            {
                "id": "cryptography",
                "name": "暗号化技術",
                "completed": False,
                "description": "公開鍵暗号、ハッシュ関数",
                "prerequisites": ["network-basics"],
                "estimated_hours": 50,
            },
            {
                "id": "penetration-testing",
                "name": "ペネトレーションテスト",
                "completed": False,
                "description": "脆弱性診断とツール活用",
                "prerequisites": ["web-security", "cryptography"],
                "estimated_hours": 70,
            },
        ],
        "edges": [
            {"from": "network-basics", "to": "web-security"},
            {"from": "network-basics", "to": "cryptography"},
            {"from": "web-security", "to": "penetration-testing"},
            {"from": "cryptography", "to": "penetration-testing"},
        ],
        "metadata": {
            "total_nodes": 4,
            "completed_nodes": 1,
            "progress_percentage": 25.0,
            "next_recommended": ["web-security", "cryptography"],
        },
    },
    SkillCategory.INFRASTRUCTURE: {
        "nodes": [
            {
                "id": "linux-basics",
                "name": "Linux基礎",
                "completed": True,
                "description": "シェル操作、ファイルシステム",
                "prerequisites": [],
                "estimated_hours": 25,
            },
            {
                "id": "docker",
                "name": "Docker/コンテナ技術",
                "completed": True,
                "description": "コンテナ化とDocker Compose",
                "prerequisites": ["linux-basics"],
                "estimated_hours": 35,
            },
            {
                "id": "kubernetes",
                "name": "Kubernetes",
                "completed": False,
                "description": "コンテナオーケストレーション",
                "prerequisites": ["docker"],
                "estimated_hours": 60,
            },
            {
                "id": "ci-cd",
                "name": "CI/CDパイプライン",
                "completed": False,
                "description": "GitHub Actions、Jenkins",
                "prerequisites": ["docker"],
                "estimated_hours": 40,
            },
            {
                "id": "iac",
                "name": "Infrastructure as Code",
                "completed": False,
                "description": "Terraform、Ansible",
                "prerequisites": ["kubernetes", "ci-cd"],
                "estimated_hours": 50,
            },
        ],
        "edges": [
            {"from": "linux-basics", "to": "docker"},
            {"from": "docker", "to": "kubernetes"},
            {"from": "docker", "to": "ci-cd"},
            {"from": "kubernetes", "to": "iac"},
            {"from": "ci-cd", "to": "iac"},
        ],
        "metadata": {
            "total_nodes": 5,
            "completed_nodes": 2,
            "progress_percentage": 40.0,
            "next_recommended": ["kubernetes", "ci-cd"],
        },
    },
    SkillCategory.DESIGN: {
        "nodes": [
            {
                "id": "design-basics",
                "name": "デザイン原則",
                "completed": True,
                "description": "色彩、タイポグラフィ、レイアウト",
                "prerequisites": [],
                "estimated_hours": 20,
            },
            {
                "id": "figma",
                "name": "Figma/デザインツール",
                "completed": True,
                "description": "プロトタイピングとデザインシステム",
                "prerequisites": ["design-basics"],
                "estimated_hours": 30,
            },
            {
                "id": "ux-research",
                "name": "UXリサーチ",
                "completed": False,
                "description": "ユーザー調査とペルソナ設計",
                "prerequisites": ["design-basics"],
                "estimated_hours": 40,
            },
            {
                "id": "accessibility",
                "name": "アクセシビリティ",
                "completed": False,
                "description": "WCAG準拠とインクルーシブ設計",
                "prerequisites": ["figma", "ux-research"],
                "estimated_hours": 35,
            },
        ],
        "edges": [
            {"from": "design-basics", "to": "figma"},
            {"from": "design-basics", "to": "ux-research"},
            {"from": "figma", "to": "accessibility"},
            {"from": "ux-research", "to": "accessibility"},
        ],
        "metadata": {
            "total_nodes": 4,
            "completed_nodes": 2,
            "progress_percentage": 50.0,
            "next_recommended": ["ux-research"],
        },
    },
    SkillCategory.GAME: {
        "nodes": [
            {
                "id": "game-math",
                "name": "ゲーム数学",
                "completed": True,
                "description": "ベクトル、行列、物理演算",
                "prerequisites": [],
                "estimated_hours": 30,
            },
            {
                "id": "unity-basics",
                "name": "Unity基礎",
                "completed": False,
                "description": "Unity EngineとC#スクリプト",
                "prerequisites": ["game-math"],
                "estimated_hours": 50,
            },
            {
                "id": "unreal-engine",
                "name": "Unreal Engine",
                "completed": False,
                "description": "UE5とBlueprint",
                "prerequisites": ["game-math"],
                "estimated_hours": 60,
            },
            {
                "id": "game-ai",
                "name": "ゲームAI",
                "completed": False,
                "description": "敵AI、ナビゲーション",
                "prerequisites": ["unity-basics", "unreal-engine"],
                "estimated_hours": 45,
            },
        ],
        "edges": [
            {"from": "game-math", "to": "unity-basics"},
            {"from": "game-math", "to": "unreal-engine"},
            {"from": "unity-basics", "to": "game-ai"},
            {"from": "unreal-engine", "to": "game-ai"},
        ],
        "metadata": {
            "total_nodes": 4,
            "completed_nodes": 1,
            "progress_percentage": 25.0,
            "next_recommended": ["unity-basics", "unreal-engine"],
        },
    },
}


def generate_skill_tree_mock(user_id: int, category: SkillCategory) -> SkillTreeResponse:
    """
    スキルツリー生成（モック実装）

    Args:
        user_id: ユーザーID（Phase 3で実際のユーザーデータ取得に使用）
        category: スキルカテゴリ

    Returns:
        SkillTreeResponse: スキルツリーデータ（固定レスポンス）
    """
    tree_data = MOCK_SKILL_TREES[category]
    return SkillTreeResponse(
        category=category,
        tree_data=tree_data,
        generated_at=datetime.now(timezone.utc),
    )


# ====================================
# 演習生成（モック）
# ====================================

# カテゴリ別演習データ（全6種類）
MOCK_QUESTS = {
    QuestCategory.WEB: {
        "id": 101,
        "title": "FastAPIで認証付きTodo API構築",
        "description": """JWT認証を実装したCRUD APIを作成し、OpenAPI仕様書を自動生成する演習。

**学習目標**:
- FastAPIの基本構造理解
- JWT認証の実装
- SQLAlchemyでのDB操作
- pytestによるテスト作成

**提出物**:
- GitHubリポジトリURL
- Swagger UIスクリーンショット
- テスト実行結果""",
        "steps": [
            "1. FastAPIプロジェクト初期化（poetry/pip）",
            "2. SQLAlchemyでTodoモデル定義（id, title, completed, user_id）",
            "3. JWT認証ミドルウェア実装（python-jose）",
            "4. CRUD エンドポイント実装（GET /todos, POST /todos, PUT /todos/{id}, DELETE /todos/{id}）",
            "5. pytestでテスト作成（カバレッジ80%以上）",
            "6. Swagger UIで動作確認",
        ],
        "estimated_time_minutes": 120,
        "resources": [
            QuestResource(
                title="FastAPI公式ドキュメント",
                url="https://fastapi.tiangolo.com/ja/",
            ),
            QuestResource(
                title="SQLAlchemy公式ドキュメント",
                url="https://docs.sqlalchemy.org/",
            ),
            QuestResource(
                title="JWT認証実装ガイド",
                url="https://fastapi.tiangolo.com/tutorial/security/",
            ),
        ],
    },
    QuestCategory.AI: {
        "id": 102,
        "title": "LangChainでRAGシステム構築",
        "description": """LangChainを使った検索拡張生成（RAG）システムの実装演習。

**学習目標**:
- LangChainの基本概念理解
- ドキュメント埋め込みとベクトル検索
- プロンプトエンジニアリング
- Streamlit UIの実装

**提出物**:
- GitHubリポジトリURL
- デモ動画（2分以内）
- 実装した検索精度レポート""",
        "steps": [
            "1. LangChainとOpenAI APIのセットアップ",
            "2. PDFドキュメント読み込みと分割（RecursiveCharacterTextSplitter）",
            "3. ChromaDBでベクトルストア構築",
            "4. RAGチェーン実装（RetrievalQA）",
            "5. Streamlitでチャットインターフェース作成",
            "6. 検索精度評価（Recall@5）",
        ],
        "estimated_time_minutes": 180,
        "resources": [
            QuestResource(
                title="LangChain公式ドキュメント",
                url="https://python.langchain.com/docs/",
            ),
            QuestResource(
                title="RAGチュートリアル",
                url="https://python.langchain.com/docs/tutorials/rag/",
            ),
            QuestResource(
                title="ChromaDB Documentation",
                url="https://docs.trychroma.com/",
            ),
        ],
    },
    QuestCategory.SECURITY: {
        "id": 103,
        "title": "Webアプリケーション脆弱性診断",
        "description": """OWASP Top 10を参考に、脆弱性診断ツールを使った演習。

**学習目標**:
- SQLインジェクション検出
- XSS（クロスサイトスクリプティング）対策
- OWASP ZAPの使い方
- 脆弱性レポート作成

**提出物**:
- 脆弱性診断レポート（PDF）
- 修正コードのPull Request
- 再診断結果""",
        "steps": [
            "1. OWASP ZAPのインストールと設定",
            "2. 対象アプリケーションの自動スキャン実行",
            "3. SQLインジェクション脆弱性の特定",
            "4. XSS脆弱性の特定と検証",
            "5. 修正コードの実装（パラメータ化クエリ、エスケープ処理）",
            "6. 修正後の再診断と結果レポート作成",
        ],
        "estimated_time_minutes": 150,
        "resources": [
            QuestResource(
                title="OWASP Top 10",
                url="https://owasp.org/www-project-top-ten/",
            ),
            QuestResource(
                title="OWASP ZAP User Guide",
                url="https://www.zaproxy.org/docs/",
            ),
            QuestResource(
                title="IPA安全なウェブサイトの作り方",
                url="https://www.ipa.go.jp/security/vuln/websecurity.html",
            ),
        ],
    },
    QuestCategory.INFRASTRUCTURE: {
        "id": 104,
        "title": "Kubernetesでマイクロサービスデプロイ",
        "description": """Kubernetesクラスタにマイクロサービスをデプロイする演習。

**学習目標**:
- Kubernetesの基本概念（Pod、Service、Deployment）
- Helmチャートの作成
- Ingressとロードバランシング
- モニタリング（Prometheus/Grafana）

**提出物**:
- k8sマニフェストファイル（GitHubリポジトリ）
- デプロイ手順書（README.md）
- Grafanaダッシュボードのスクリーンショット""",
        "steps": [
            "1. Minikubeまたはk3sのローカルクラスタ起動",
            "2. Dockerイメージのビルドとプッシュ（Docker Hub）",
            "3. Deployment、Serviceマニフェスト作成",
            "4. Ingressコントローラー設定（nginx-ingress）",
            "5. Prometheus + Grafanaのインストール（Helm）",
            "6. カスタムダッシュボード作成とメトリクス確認",
        ],
        "estimated_time_minutes": 200,
        "resources": [
            QuestResource(
                title="Kubernetes Documentation",
                url="https://kubernetes.io/docs/home/",
            ),
            QuestResource(
                title="Helm公式ドキュメント",
                url="https://helm.sh/docs/",
            ),
            QuestResource(
                title="Prometheus Operator",
                url="https://prometheus-operator.dev/",
            ),
        ],
    },
    QuestCategory.DESIGN: {
        "id": 105,
        "title": "アクセシブルなUI/UXデザイン実践",
        "description": """WCAG 2.2準拠のアクセシブルなWebアプリUIを設計する演習。

**学習目標**:
- WAI-ARIAの実装
- キーボードナビゲーション対応
- スクリーンリーダーテスト
- カラーコントラスト比の調整

**提出物**:
- Figmaデザインファイル（共有リンク）
- アクセシビリティチェックリスト（Excel/Google Sheets）
- スクリーンリーダー操作デモ動画""",
        "steps": [
            "1. Figmaでワイヤーフレーム作成（ダッシュボード画面）",
            "2. WCAG 2.2 AAレベルのカラーコントラスト確認",
            "3. キーボードナビゲーション順序の設計",
            "4. WAI-ARIA属性の設定（role, aria-label等）",
            "5. axe DevToolsで自動テスト実行",
            "6. NVDA/JAWSでスクリーンリーダーテスト",
        ],
        "estimated_time_minutes": 160,
        "resources": [
            QuestResource(
                title="WCAG 2.2 Guidelines",
                url="https://www.w3.org/WAI/WCAG22/quickref/",
            ),
            QuestResource(
                title="WAI-ARIA Authoring Practices",
                url="https://www.w3.org/WAI/ARIA/apg/",
            ),
            QuestResource(
                title="axe DevTools Documentation",
                url="https://www.deque.com/axe/devtools/",
            ),
        ],
    },
    QuestCategory.GAME: {
        "id": 106,
        "title": "Unity 2Dシューティングゲーム制作",
        "description": """Unityで2Dシューティングゲームを制作し、敵AIを実装する演習。

**学習目標**:
- Unity 2Dゲームの基本構造
- Rigidbody2Dによる物理演算
- 敵AIの実装（追跡、回避）
- パーティクルエフェクト

**提出物**:
- GitHubリポジトリ（Unityプロジェクト）
- WebGL ビルド（itch.io公開）
- プレイ動画（YouTube/ニコニコ動画）""",
        "steps": [
            "1. Unityプロジェクト作成（2D テンプレート）",
            "2. プレイヤー移動とシューティング実装（Input System）",
            "3. 敵キャラのスポーン管理（Object Pooling）",
            "4. 敵AI実装（NavMeshによる追跡、レイキャストによる回避）",
            "5. パーティクルエフェクト追加（爆発、弾痕）",
            "6. WebGLビルドとitch.io公開",
        ],
        "estimated_time_minutes": 240,
        "resources": [
            QuestResource(
                title="Unity Learn - 2D Game Kit",
                url="https://learn.unity.com/project/2d-game-kit",
            ),
            QuestResource(
                title="Input System Documentation",
                url="https://docs.unity3d.com/Packages/com.unity.inputsystem@latest",
            ),
            QuestResource(
                title="NavMesh Tutorial",
                url="https://docs.unity3d.com/Manual/nav-BuildingNavMesh.html",
            ),
        ],
    },
}


def generate_quest_mock(
    user_id: int, category: QuestCategory, difficulty: int, document_text: str
) -> QuestGenerationResponse:
    """
    演習生成（モック実装）

    Args:
        user_id: ユーザーID（Phase 3で実際のユーザーデータ取得に使用）
        category: クエストカテゴリ
        difficulty: 難易度（0-9、Phase 3でランクに基づく調整に使用）
        document_text: 参考ドキュメント（Phase 3でRAGに使用、最大100KB）

    Returns:
        QuestGenerationResponse: 演習データ（固定レスポンス）

    Note:
        Phase 3移行時の考慮事項:
        - document_text を RAG（Retrieval-Augmented Generation）で使用
        - difficulty に基づいて演習の複雑度を調整
        - user_id から Profile テーブルの学習履歴を取得し、パーソナライズ
    """
    quest_data = MOCK_QUESTS[category]
    return QuestGenerationResponse(
        id=quest_data["id"],
        title=quest_data["title"],
        description=quest_data["description"],
        difficulty=difficulty,  # リクエストの難易度を反映
        category=category,
        is_generated=True,
        steps=quest_data["steps"],
        estimated_time_minutes=quest_data["estimated_time_minutes"],
        resources=quest_data["resources"],
        created_at=datetime.now(timezone.utc),
    )
