"""
モックAPIエンドポイントのテスト - Issue #35, #54, #74

Test Coverage:
1. スキルツリー生成エンドポイント（POST /analyze/skill-tree）
   - 全6カテゴリのデータ存在確認
   - tree_data JSON構造の検証（nodes, edges, metadata）
   - バリデーションエラー処理
   - Note: Issue #74で認証必須に変更（JWT Cookie使用）

2. 演習生成エンドポイント（/analyze/quest）
  - カテゴリ別レスポンス確認
   - difficulty範囲（0-9）の検証
   - バリデーションエラー処理
"""

import pytest
from datetime import datetime, UTC
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.models.enums import QuestCategory, SkillCategory
from app.schemas.analyze import SkillTreeResponse
from app.db.session import get_db


@pytest.fixture()
def client(db):
    """テストクライアント（DBセッションを注入）"""

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, follow_redirects=False) as c:
        yield c
    app.dependency_overrides.clear()


def _setup_authenticated_user(client, db):
    """認証済みテストユーザーをセットアップしCookieを取得"""
    from app.crud.user import create_user
    from app.schemas.user import UserCreate

    # テストユーザー作成
    create_user(
        db, UserCreate(username="test_skill_tree_mock_user", password="testpass123")
    )

    # ログインしてCookieを取得
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_skill_tree_mock_user", "password": "testpass123"},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"

    # CookieをTestClient用に返す
    return {"access_token": response.cookies.get("access_token")}


# ====================================
# スキルツリー生成エンドポイント
# ====================================


class TestSkillTreeGeneration:
    """スキルツリー生成API（POST /analyze/skill-tree 認証必須）のテスト"""

    @pytest.mark.parametrize(
        "category",
        [
            SkillCategory.WEB,
            SkillCategory.AI,
            SkillCategory.SECURITY,
            SkillCategory.INFRASTRUCTURE,
            SkillCategory.DESIGN,
            SkillCategory.GAME,
        ],
    )
    def test_generate_skill_tree_all_categories(
        self, client, db, category: SkillCategory
    ):
        """全6カテゴリでスキルツリーが正常に生成されることを確認（AI実装モック + 認証必須）"""
        # 認証済みユーザーをセットアップしCookie取得
        cookies = _setup_authenticated_user(client, db)

        # Mock: AI実装をモック化
        mock_tree_data = {
            "nodes": [
                {
                    "id": f"{category.value}_test_node",
                    "name": "Test Node",
                    "completed": False,
                    "description": "Test description",
                    "prerequisites": [],
                    "estimated_hours": 10,
                }
            ],
            "edges": [],
            "metadata": {
                "total_nodes": 1,
                "completed_nodes": 0,
                "progress_percentage": 0.0,
                "next_recommended": [],
            },
        }

        mock_response = SkillTreeResponse(
            category=category.value,
            tree_data=mock_tree_data,
            generated_at=datetime.now(UTC),
        )

        with patch(
            "app.api.endpoints.analyze.generate_skill_tree_ai",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            response = client.post(
                "/api/v1/analyze/skill-tree",
                json={
                    "category": category.value,
                },
                cookies=cookies,
            )

        assert response.status_code == 200
        data = response.json()

        # レスポンススキーマ検証
        assert "category" in data
        assert "tree_data" in data
        assert "generated_at" in data
        assert data["category"] == category.value

        # tree_data JSON構造検証
        tree_data = data["tree_data"]
        assert "nodes" in tree_data
        assert "edges" in tree_data
        assert "metadata" in tree_data

        # nodes配列の検証
        assert isinstance(tree_data["nodes"], list)
        assert len(tree_data["nodes"]) > 0
        for node in tree_data["nodes"]:
            assert "id" in node
            assert "name" in node
            assert "completed" in node
            assert "description" in node
            assert "prerequisites" in node
            assert "estimated_hours" in node
            assert isinstance(node["completed"], bool)
            assert isinstance(node["prerequisites"], list)
            assert isinstance(node["estimated_hours"], int)

        # edges配列の検証
        assert isinstance(tree_data["edges"], list)
        for edge in tree_data["edges"]:
            assert "from" in edge
            assert "to" in edge

        # metadata検証
        metadata = tree_data["metadata"]
        assert "total_nodes" in metadata
        assert "completed_nodes" in metadata
        assert "progress_percentage" in metadata
        assert "next_recommended" in metadata
        assert isinstance(metadata["total_nodes"], int)
        assert isinstance(metadata["completed_nodes"], int)
        assert isinstance(metadata["progress_percentage"], (int, float))
        assert isinstance(metadata["next_recommended"], list)
        assert metadata["total_nodes"] == len(tree_data["nodes"])

    def test_skill_tree_invalid_category(self, client, db):
        """categoryが無効な場合のバリデーションエラー"""
        # 認証済みユーザーをセットアップしCookie取得
        cookies = _setup_authenticated_user(client, db)

        response = client.post(
            "/api/v1/analyze/skill-tree",
            json={
                "category": "invalid_category",  # 存在しないカテゴリ
            },
            cookies=cookies,
        )

        assert response.status_code == 422  # Unprocessable Entity

    def test_skill_tree_missing_required_fields(self, client, db):
        """必須フィールド（category）が欠けている場合のエラー"""
        # 認証済みユーザーをセットアップしCookie取得
        cookies = _setup_authenticated_user(client, db)

        response = client.post(
            "/api/v1/analyze/skill-tree",
            json={},
            cookies=cookies,
        )

        assert response.status_code == 422  # Unprocessable Entity

    def test_skill_tree_without_authentication(self):
        """認証なしでアクセスした場合は401エラー"""
        # 新しいクライアント（認証なし、DBセッション注入なし）
        unauthenticated_client = TestClient(app)

        response = unauthenticated_client.post(
            "/api/v1/analyze/skill-tree",
            json={"category": "web"},
        )

        assert response.status_code == 401  # Unauthorized


# ====================================
# 演習生成エンドポイント
# ====================================


class TestQuestGeneration:
    """演習生成API（/analyze/quest）のテスト"""

    @pytest.mark.parametrize(
        "category",
        [
            QuestCategory.WEB,
            QuestCategory.AI,
            QuestCategory.SECURITY,
            QuestCategory.INFRASTRUCTURE,
            QuestCategory.DESIGN,
            QuestCategory.GAME,
        ],
    )
    def test_generate_quest_all_categories(self, client, category: QuestCategory):
        """全6カテゴリで演習が正常に生成されることを確認"""
        # Mock: ユーザー情報
        mock_user = type("User", (), {"rank": 3})()

        # Mock: LLM実装をモック化
        mock_llm_result = {
            "title": f"{category.value.capitalize()} Quest",
            "difficulty": "intermediate",
            "learning_objectives": ["目標1", "目標2"],
            "steps": [
                {
                    "step_number": 1,
                    "title": "Step 1",
                    "description": "Description 1",
                },
                {
                    "step_number": 2,
                    "title": "Step 2",
                    "description": "Description 2",
                },
            ],
            "estimated_time_minutes": 60,
            "resources": [{"title": "Resource 1", "url": "https://example.com"}],
        }

        with patch("app.api.endpoints.analyze.get_user", return_value=mock_user), patch(
            "app.api.endpoints.analyze.generate_handson_quest",
            new_callable=AsyncMock,
            return_value=mock_llm_result,
        ):
            response = client.post(
                "/api/v1/analyze/quest",
                json={
                    "user_id": 1,
                    "category": category.value,
                    "difficulty": 4,
                    "document_text": "サンプルドキュメント",
                },
            )

        assert response.status_code == 200
        data = response.json()

        # レスポンススキーマ検証
        assert "id" in data
        assert "title" in data
        assert "description" in data
        assert "difficulty" in data
        assert "category" in data
        assert "is_generated" in data
        assert "steps" in data
        assert "estimated_time_minutes" in data
        assert "resources" in data
        assert "created_at" in data

        assert data["category"] == category.value
        assert data["difficulty"] == 4
        assert data["is_generated"] is True

        # steps配列の検証
        assert isinstance(data["steps"], list)
        assert len(data["steps"]) > 0
        for step in data["steps"]:
            assert isinstance(step, str)
            assert len(step) > 0

        # estimated_time_minutes検証
        assert isinstance(data["estimated_time_minutes"], int)
        assert data["estimated_time_minutes"] > 0

        # resources配列の検証
        assert isinstance(data["resources"], list)
        assert len(data["resources"]) > 0
        for resource in data["resources"]:
            assert "title" in resource
            assert "url" in resource
            assert isinstance(resource["title"], str)
            assert isinstance(resource["url"], str)
            assert resource["url"].startswith("http")  # URLの基本検証

    @pytest.mark.parametrize("difficulty", [0, 1, 4, 5, 9])
    def test_generate_quest_valid_difficulty_range(self, client, difficulty: int):
        """difficulty範囲（0-9）が正しいことを確認"""
        # Mock: ユーザー情報とLLM実装
        mock_user = type("User", (), {"rank": 3})()
        mock_llm_result = {
            "title": "Test Quest",
            "difficulty": "intermediate",
            "learning_objectives": ["目標"],
            "steps": [{"step_number": 1, "title": "Step", "description": "Desc"}],
            "estimated_time_minutes": 60,
            "resources": [{"title": "Resource", "url": "https://example.com"}],
        }

        with patch("app.api.endpoints.analyze.get_user", return_value=mock_user), patch(
            "app.api.endpoints.analyze.generate_handson_quest",
            new_callable=AsyncMock,
            return_value=mock_llm_result,
        ):
            response = client.post(
                "/api/v1/analyze/quest",
                json={
                    "user_id": 1,
                    "category": "web",
                    "difficulty": difficulty,
                    "document_text": "",
                },
            )

        assert response.status_code == 200
        data = response.json()
        # LLM実装では、difficultyはマッピングされるため、必ずしも入力と同じではない
        assert data["difficulty"] in range(0, 10)

    @pytest.mark.parametrize("invalid_difficulty", [-1, 10, 100])
    def test_generate_quest_invalid_difficulty(self, client, invalid_difficulty: int):
        """difficulty範囲外（<0 or >9）の場合のバリデーションエラー"""
        response = client.post(
            "/api/v1/analyze/quest",
            json={
                "user_id": 1,
                "category": "web",
                "difficulty": invalid_difficulty,
                "document_text": "",
            },
        )

        assert response.status_code == 422  # Unprocessable Entity

    def test_generate_quest_document_text_size_limit(self, client):
        """document_textのサイズ制限（100KB）を確認"""
        # Mock: ユーザー情報とLLM実装
        mock_user = type("User", (), {"rank": 3})()
        mock_llm_result = {
            "title": "Test Quest",
            "difficulty": "intermediate",
            "learning_objectives": ["目標"],
            "steps": [{"step_number": 1, "title": "Step", "description": "Desc"}],
            "estimated_time_minutes": 60,
            "resources": [{"title": "Resource", "url": "https://example.com"}],
        }

        # 100KB以下のテキスト（正常）
        small_text = "A" * 50000  # 50KB
        with patch("app.api.endpoints.analyze.get_user", return_value=mock_user), patch(
            "app.api.endpoints.analyze.generate_handson_quest",
            new_callable=AsyncMock,
            return_value=mock_llm_result,
        ):
            response = client.post(
                "/api/v1/analyze/quest",
                json={
                    "user_id": 1,
                    "category": "web",
                    "difficulty": 4,
                    "document_text": small_text,
                },
            )
        assert response.status_code == 200

        # 100KB超のテキスト（エラー）
        large_text = "A" * 150000  # 150KB
        response = client.post(
            "/api/v1/analyze/quest",
            json={
                "user_id": 1,
                "category": "web",
                "difficulty": 4,
                "document_text": large_text,
            },
        )
        assert response.status_code == 422  # Unprocessable Entity

    def test_generate_quest_invalid_category(self, client):
        """categoryが無効な場合のバリデーションエラー"""
        response = client.post(
            "/api/v1/analyze/quest",
            json={
                "user_id": 1,
                "category": "invalid_category",
                "difficulty": 4,
                "document_text": "",
            },
        )

        assert response.status_code == 422  # Unprocessable Entity

    def test_generate_quest_missing_required_fields(self, client):
        """必須フィールドが欠けている場合のエラー"""
        response = client.post(
            "/api/v1/analyze/quest",
            json={
                "user_id": 1,
                # category, difficulty が欠けている
                "document_text": "",
            },
        )

        assert response.status_code == 422  # Unprocessable Entity

    def test_generate_quest_optional_document_text(self, client):
        """document_textは省略可能であることを確認"""
        # Mock: ユーザー情報とLLM実装
        mock_user = type("User", (), {"rank": 3})()
        mock_llm_result = {
            "title": "Test Quest",
            "difficulty": "intermediate",
            "learning_objectives": ["目標"],
            "steps": [{"step_number": 1, "title": "Step", "description": "Desc"}],
            "estimated_time_minutes": 60,
            "resources": [{"title": "Resource", "url": "https://example.com"}],
        }

        with patch("app.api.endpoints.analyze.get_user", return_value=mock_user), patch(
            "app.api.endpoints.analyze.generate_handson_quest",
            new_callable=AsyncMock,
            return_value=mock_llm_result,
        ):
            response = client.post(
                "/api/v1/analyze/quest",
                json={
                    "user_id": 1,
                    "category": "web",
                    "difficulty": 4,
                    # document_text 省略
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
