"""
モックAPIエンドポイントのテスト - Issue #35, #54

Test Coverage:
1. スキルツリー生成エンドポイント（/analyze/skill-tree）
   - 全6カテゴリのデータ存在確認
   - tree_data JSON構造の検証（nodes, edges, metadata）
   - バリデーションエラー処理
   - Note: Issue #54でAI実装に移行、モック化してテスト

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

client = TestClient(app)


# ====================================
# スキルツリー生成エンドポイント
# ====================================


class TestSkillTreeGeneration:
    """スキルツリー生成API（/analyze/skill-tree）のテスト"""

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
    def test_generate_skill_tree_all_categories(self, category: SkillCategory):
        """全6カテゴリでスキルツリーが正常に生成されることを確認（AI実装モック）"""
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
                    "user_id": 1,
                    "category": category.value,
                },
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

    def test_skill_tree_invalid_user_id(self):
        """user_idが無効な場合のバリデーションエラー"""
        response = client.post(
            "/api/v1/analyze/skill-tree",
            json={
                "user_id": 0,  # 0は無効（gt=0）
                "category": "web",
            },
        )

        assert response.status_code == 422  # Unprocessable Entity

    def test_skill_tree_invalid_category(self):
        """categoryが無効な場合のバリデーションエラー"""
        response = client.post(
            "/api/v1/analyze/skill-tree",
            json={
                "user_id": 1,
                "category": "invalid_category",  # 存在しないカテゴリ
            },
        )

        assert response.status_code == 422  # Unprocessable Entity

    def test_skill_tree_missing_required_fields(self):
        """必須フィールドが欠けている場合のエラー"""
        response = client.post(
            "/api/v1/analyze/skill-tree",
            json={
                "user_id": 1,
                # category が欠けている
            },
        )

        assert response.status_code == 422  # Unprocessable Entity


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
    def test_generate_quest_all_categories(self, category: QuestCategory):
        """全6カテゴリで演習が正常に生成されることを確認"""
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
    def test_generate_quest_valid_difficulty_range(self, difficulty: int):
        """difficulty範囲（0-9）が正しいことを確認"""
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
        assert data["difficulty"] == difficulty

    @pytest.mark.parametrize("invalid_difficulty", [-1, 10, 100])
    def test_generate_quest_invalid_difficulty(self, invalid_difficulty: int):
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

    def test_generate_quest_document_text_size_limit(self):
        """document_textのサイズ制限（100KB）を確認"""
        # 100KB以下のテキスト（正常）
        small_text = "A" * 50000  # 50KB
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

    def test_generate_quest_invalid_category(self):
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

    def test_generate_quest_missing_required_fields(self):
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

    def test_generate_quest_optional_document_text(self):
        """document_textは省略可能であることを確認"""
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
