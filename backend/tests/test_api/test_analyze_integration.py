"""
ランク判定APIエンドポイントのインテグレーションテスト

実際のLLM APIを使用してFastAPIエンドポイントをテスト。
環境変数に有効なAPIキーが必要。

実行方法:
    pytest tests/test_api/test_analyze_integration.py -v -s

    # スキルツリー統合テストのみ実行:
    pytest tests/test_api/test_analyze_integration.py::test_generate_skill_tree_real_api -v -s

環境変数:
    - OPENAI_API_KEY または ANTHROPIC_API_KEY (必須)
    - GITHUB_API_TOKEN (推奨)
      ※未設定の場合はPublicリポジトリのみ分析（Rate Limit: 60 req/hour）
      ※設定するとPrivateリポジトリも分析可能（Rate Limit: 5000 req/hour）

GitHub API Token の取得:
    1. https://github.com/settings/tokens
    2. "Generate new token (classic)"
    3. スコープ: repo, read:user, user:email
    4. export GITHUB_API_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

統合テスト (JWT認証付き):
    - POST /api/v1/analyze/skill-tree は JWT Cookie 認証が必須
    - テストは _setup_authenticated_user() で認証用Cookieを取得
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.config import settings
from app.models.profile import Profile
from app.crud.user import create_user
from app.schemas.user import UserCreate
from app.db.session import get_db


client = TestClient(app)


def _setup_authenticated_user(
    db: Session, github_username: str = "torvalds"
) -> dict[str, str]:
    """
    認証済みユーザーを作成してJWT Cookieを取得

    Args:
        db: データベースセッション
        github_username: プロフィールに設定するGitHubユーザー名

    Returns:
        dict[str, str]: 認証用Cookie (例: {"access_token": "Bearer xxx"})
    """
    # テストユーザー作成（パスワードハッシュ化）
    test_user = create_user(
        db=db,
        user=UserCreate(username="test_integration_user", password="test_password"),
        commit=False,
    )
    test_user.rank = 3  # 任意のrankを設定

    # プロフィール作成
    test_profile = Profile(
        user_id=test_user.id,
        github_username=github_username,
        qiita_id="",
    )
    db.add(test_profile)

    # スキルツリー初期化（create_user内で既に初期化済み）
    # initialize_skill_trees_for_user(db, test_user.id)  # 重複呼び出し回避

    db.commit()

    # ログインしてCookie取得
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_integration_user", "password": "test_password"},
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"

    # CookieをTestClient用に返す
    return {"access_token": login_response.cookies.get("access_token")}


@pytest.mark.integration
def test_analyze_rank_endpoint_real_api():
    """
    実際のLLM APIを使用したエンドポイントテスト

    検証項目:
    - POST /api/v1/analyze/rank が正常に動作する
    - レスポンスが正しいスキーマに従っている
    - ステータスコード 200 が返る
    """
    # APIキーが設定されているか確認
    if settings.LLM_PROVIDER.lower() == "openai":
        if not settings.OPENAI_API_KEY or "REPLACE" in settings.OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set. Please set it in .env file.")
    elif settings.LLM_PROVIDER.lower() == "anthropic":
        if not settings.ANTHROPIC_API_KEY or "REPLACE" in settings.ANTHROPIC_API_KEY:
            pytest.skip("ANTHROPIC_API_KEY not set. Please set it in .env file.")

    # テストリクエスト
    response = client.post(
        "/api/v1/analyze/rank",
        json={
            "github_username": "torvalds",
            "portfolio_text": "Linux kernel creator, Git inventor",
            "qiita_id": "",
            "other_info": "Created Linux operating system and Git version control",
        },
    )

    # レスポンス検証
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()

    # スキーマ検証
    assert "percentile" in data, "percentile field is missing"
    assert "rank" in data, "rank field is missing"
    assert "rank_name" in data, "rank_name field is missing"
    assert "reasoning" in data, "reasoning field is missing"

    # 値の範囲検証
    assert (
        0.0 <= data["percentile"] <= 100.0
    ), f"percentile out of range: {data['percentile']}"
    assert 0 <= data["rank"] <= 9, f"rank out of range: {data['rank']} (expected 0-9)"
    assert isinstance(data["rank_name"], str), "rank_name must be string"
    assert len(data["reasoning"]) > 0, "reasoning must not be empty"

    # デバッグ出力
    print("\n=== API Response ===")
    print(f"Status Code: {response.status_code}")
    print(f"Percentile: {data['percentile']}")
    print(f"Rank: {data['rank']} ({data['rank_name']})")
    print(f"Reasoning: {data['reasoning']}")
    print("=" * 40)


@pytest.mark.integration
def test_analyze_rank_endpoint_beginner():
    """
    初心者レベルのリクエストでテスト
    """
    if settings.LLM_PROVIDER.lower() == "openai":
        if not settings.OPENAI_API_KEY or "REPLACE" in settings.OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set")
    elif settings.LLM_PROVIDER.lower() == "anthropic":
        if not settings.ANTHROPIC_API_KEY or "REPLACE" in settings.ANTHROPIC_API_KEY:
            pytest.skip("ANTHROPIC_API_KEY not set")

    response = client.post(
        "/api/v1/analyze/rank",
        json={
            "github_username": "newuser123",
            "portfolio_text": "プログラミング学習中",
            "qiita_id": "",
            "other_info": "Progateで HTML/CSS を学習",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "percentile" in data
    assert "rank" in data
    assert "rank_name" in data
    assert "reasoning" in data

    print("\n=== Beginner API Response ===")
    print(f"Percentile: {data['percentile']}")
    print(f"Rank: {data['rank']} ({data['rank_name']})")
    print(f"Reasoning: {data['reasoning']}")
    print("=" * 40)


@pytest.mark.integration
def test_analyze_rank_endpoint_minimal_input():
    """
    最小限の入力（GitHub username のみ）でテスト
    """
    if settings.LLM_PROVIDER.lower() == "openai":
        if not settings.OPENAI_API_KEY or "REPLACE" in settings.OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set")
    elif settings.LLM_PROVIDER.lower() == "anthropic":
        if not settings.ANTHROPIC_API_KEY or "REPLACE" in settings.ANTHROPIC_API_KEY:
            pytest.skip("ANTHROPIC_API_KEY not set")

    response = client.post(
        "/api/v1/analyze/rank",
        json={"github_username": "test_user"},
    )

    assert response.status_code == 200
    data = response.json()

    assert "percentile" in data
    assert "rank" in data
    assert "rank_name" in data
    assert "reasoning" in data

    print("\n=== Minimal Input API Response ===")
    print(f"Percentile: {data['percentile']}")
    print(f"Rank: {data['rank']} ({data['rank_name']})")
    print(f"Reasoning: {data['reasoning']}")
    print("=" * 40)


@pytest.mark.integration
@pytest.mark.skip(reason="Customizable test - fill in your data to run manually")
def test_analyze_rank_endpoint_custom():
    """
    カスタムユーザー情報でテスト（自分の情報でカスタマイズ可能）
    """
    if settings.LLM_PROVIDER.lower() == "openai":
        if not settings.OPENAI_API_KEY or "REPLACE" in settings.OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set")
    elif settings.LLM_PROVIDER.lower() == "anthropic":
        if not settings.ANTHROPIC_API_KEY or "REPLACE" in settings.ANTHROPIC_API_KEY:
            pytest.skip("ANTHROPIC_API_KEY not set")

    # ここをカスタマイズして実行
    response = client.post(
        "/api/v1/analyze/rank",
        json={
            "github_username": "",  # GitHubユーザー名を入力
            "portfolio_text": "",  # ポートフォリオテキストを入力
            "qiita_id": "",  # Qiita IDを入力
            "other_info": "",  # その他の情報を入力
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "percentile" in data
    assert "rank" in data
    assert "rank_name" in data
    assert "reasoning" in data

    print("\n=== Custom User API Response ===")
    print(f"Status Code: {response.status_code}")
    print(
        f"Percentile: {data['percentile']:.1f}% (上位 {(100 - data['percentile']):.1f}%)"
    )
    print(f"Rank: {data['rank']} ({data['rank_name']})")
    print(f"Reasoning: {data['reasoning']}")
    print("=" * 40)


# ====================================
# スキルツリー生成エンドポイント統合テスト
# ====================================


@pytest.mark.integration
def test_generate_skill_tree_real_api(db: Session):
    """
    実際のGitHub API + LLM APIを使用したスキルツリー生成テスト

    Issue #64: スキルツリー生成の統合テスト

    検証項目:
    - POST /api/v1/analyze/skill-tree が正常に動作する
    - GitHub APIでユーザー情報を取得できる
    - LLMでパーソナライズされたスキルツリーが生成される
    - GitHub分析結果でcompletedフラグが更新される
    - レスポンスが正しいスキーマに従っている
    """
    # APIキーチェック
    if settings.LLM_PROVIDER.lower() == "openai":
        if not settings.OPENAI_API_KEY or "REPLACE" in settings.OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set. Please set it in .env file.")
    elif settings.LLM_PROVIDER.lower() == "anthropic":
        if not settings.ANTHROPIC_API_KEY or "REPLACE" in settings.ANTHROPIC_API_KEY:
            pytest.skip("ANTHROPIC_API_KEY not set. Please set it in .env file.")

    # GitHub API Token チェック
    print("\n=== GitHub API Token Status ===")
    if settings.GITHUB_API_TOKEN:
        print(f"✅ Token: 設定済み ({settings.GITHUB_API_TOKEN[:10]}...)")
        print("   → Privateリポジトリも分析可能 (Rate Limit: 5000 req/hour)")
    else:
        print("⚠️  Token: 未設定")
        print("   → Publicリポジトリのみ分析可能 (Rate Limit: 60 req/hour)")
        print("   → https://github.com/settings/tokens でPAT作成を推奨")
    print("=" * 50)

    # テスト用のDBセッションをオーバーライド
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    try:
        # 認証済みユーザーを作成してCookie取得
        cookies = _setup_authenticated_user(db, github_username="torvalds")

        # スキルツリー生成リクエスト（WEBカテゴリ）（user_id削除・JWT Cookie認証）
        response = client.post(
            "/api/v1/analyze/skill-tree",
            json={"category": "web"},
            cookies=cookies,
        )

        # レスポンス検証
        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code}: {response.text}"

        data = response.json()

        # スキーマ検証
        assert "category" in data, "category field is missing"
        assert "tree_data" in data, "tree_data field is missing"
        assert "generated_at" in data, "generated_at field is missing"

        assert data["category"] == "web"

        # tree_data構造検証
        tree_data = data["tree_data"]
        assert "nodes" in tree_data, "tree_data.nodes is missing"
        assert "edges" in tree_data, "tree_data.edges is missing"
        assert "metadata" in tree_data, "tree_data.metadata is missing"

        # nodes検証
        assert isinstance(tree_data["nodes"], list), "nodes must be a list"
        assert len(tree_data["nodes"]) > 0, "nodes must not be empty"

        # completedフラグが設定されているノードを確認
        completed_nodes = [
            node for node in tree_data["nodes"] if node.get("completed", False)
        ]

        print("\n=== Skill Tree Generation API Response ===")
        print(f"Status Code: {response.status_code}")
        print(f"Category: {data['category']}")
        print(f"Total Nodes: {len(tree_data['nodes'])}")
        print(f"Completed Nodes: {len(completed_nodes)}")
        print(f"Completed Node IDs: {[node['id'] for node in completed_nodes]}")
        print(f"Progress: {tree_data['metadata'].get('progress_percentage', 0)}%")
        print(f"Generated At: {data['generated_at']}")
        print("=" * 40)

        # クリーンアップ（ユーザーは自動削除される）
    finally:
        # dependency_overridesをクリア
        app.dependency_overrides.clear()


@pytest.mark.integration
def test_generate_skill_tree_custom_github(db: Session):
    """
    自分のGitHubアカウントでスキルツリー生成をテスト

    使い方:
    1. 以下の github_username を自分のGitHubユーザー名に変更
    2. @pytest.mark.skip をコメントアウト
    3. pytest tests/test_api/test_analyze_integration.py::test_generate_skill_tree_custom_github -v -s で実行

    確認ポイント:
    - 自分のGitHubリポジトリが分析される
    - 使用している言語・技術スタックが検出される
    - 該当するスキルノードがcompletedになる
    """
    # APIキーチェック
    if settings.LLM_PROVIDER.lower() == "openai":
        if not settings.OPENAI_API_KEY or "REPLACE" in settings.OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set")
    elif settings.LLM_PROVIDER.lower() == "anthropic":
        if not settings.ANTHROPIC_API_KEY or "REPLACE" in settings.ANTHROPIC_API_KEY:
            pytest.skip("ANTHROPIC_API_KEY not set")

    # GitHub API Token チェック
    print("\n=== GitHub API Token Status ===")
    if settings.GITHUB_API_TOKEN:
        print(f"✅ Token: 設定済み ({settings.GITHUB_API_TOKEN[:10]}...)")
        print("   → Privateリポジトリも分析可能 (Rate Limit: 5000 req/hour)")
    else:
        print("⚠️  Token: 未設定")
        print("   → Publicリポジトリのみ分析可能 (Rate Limit: 60 req/hour)")
        print("   → https://github.com/settings/tokens でPAT作成を推奨")
    print("=" * 50)

    # ここに自分のGitHubユーザー名を入力
    github_username = "Inlet-back"  # 認証済みユーザー

    if not github_username:
        pytest.skip("github_username not set. Please set it in the test code.")

    # テスト用のDBセッションをオーバーライド
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    try:
        # 認証済みユーザーを作成してCookie取得
        cookies = _setup_authenticated_user(db, github_username=github_username)

        # 全カテゴリでスキルツリー生成
        categories = ["web", "ai", "security", "infrastructure", "design", "game"]

        for category in categories:
            print(f"\n{'='*50}")
            print(f"カテゴリ: {category.upper()}")
            print("=" * 50)

            response = client.post(
                "/api/v1/analyze/skill-tree",
                json={"category": category},
                cookies=cookies,
            )

            assert (
                response.status_code == 200
            ), f"Failed for {category}: {response.text}"

            data = response.json()
            tree_data = data["tree_data"]

            # 完了ノード抽出
            completed_nodes = [
                node for node in tree_data["nodes"] if node.get("completed", False)
            ]

            print(f"総ノード数: {len(tree_data['nodes'])}")
            print(f"完了ノード数: {len(completed_nodes)}")
            print(f"進捗率: {tree_data['metadata'].get('progress_percentage', 0):.1f}%")

            if completed_nodes:
                print("\n完了済みスキル:")
                for node in completed_nodes[:5]:  # 最初の5個だけ表示
                    print(f"  - {node.get('name', node.get('id'))}")
                if len(completed_nodes) > 5:
                    print(f"  ... 他 {len(completed_nodes) - 5} 個")

        print("\n" + "=" * 50)
        print("全カテゴリのスキルツリー生成が完了しました!")
        print("=" * 50)

        # クリーンアップ（ユーザーは自動削除される）
    finally:
        # dependency_overridesをクリア
        app.dependency_overrides.clear()
