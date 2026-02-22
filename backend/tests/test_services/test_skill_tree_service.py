"""
スキルツリーサービスのテスト

Issue #54: AI実装Phase 3 - スキルツリー生成（LLMパーソナライゼーション）
"""

import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.models.enums import SkillCategory
from app.models.profile import Profile
from app.models.skill_tree import SkillTree
from app.models.user import User
from app.services.skill_tree_service import (
    generate_skill_tree_ai,
    _is_cache_valid,
    _load_baseline_json,
    _build_skill_tree_prompt,
)


class TestSkillTreeService:
    """スキルツリーAI実装のテスト"""

    @pytest.mark.asyncio
    async def test_generate_skill_tree_ai_with_cache(self, db: Session):
        """キャッシュが有効な場合はDBから返却"""
        # Arrange: キャッシュが有効なSkillTreeを準備
        category = SkillCategory.WEB

        # User→Profileを作成
        user = User(username="test_user", rank=4)
        db.add(user)
        db.flush()

        profile = Profile(
            user_id=user.id,
            github_username="testuser",
        )
        db.add(profile)

        # SkillTreeを作成（5分前に生成）
        tree_data = {
            "nodes": [{"id": "test-node", "name": "Test", "completed": False}],
            "edges": [],
            "metadata": {
                "total_nodes": 1,
                "completed_nodes": 0,
                "progress_percentage": 0.0,
                "next_recommended": [],
            },
        }
        skill_tree = SkillTree(
            user_id=user.id,
            category=category.value,
            tree_data=tree_data,
            generated_at=datetime.now(UTC) - timedelta(minutes=5),
        )
        db.add(skill_tree)
        db.commit()

        # Mock: settings.SKILL_TREE_CACHE_MINUTES = 10 (5分前のキャッシュが有効)
        with patch("app.services.skill_tree_service.settings") as mock_settings:
            mock_settings.SKILL_TREE_CACHE_MINUTES = 10
            # Act: generate_skill_tree_ai を呼び出し
            result = await generate_skill_tree_ai(user.id, category, db)

        # Assert: キャッシュから返却されることを確認
        assert result.category == category.value
        assert result.tree_data == tree_data
        assert result.generated_at is not None

    @pytest.mark.asyncio
    async def test_generate_skill_tree_ai_regenerate(self, db: Session):
        """キャッシュが古い場合はLLM呼び出し"""
        # Arrange: キャッシュが古いSkillTreeを準備
        category = SkillCategory.AI

        # User→Profileを作成
        user = User(username="test_user", rank=5)
        db.add(user)
        db.flush()

        profile = Profile(
            user_id=user.id,
            github_username="testuser",
        )
        db.add(profile)

        # SkillTreeを作成（15分前に生成 → キャッシュ期限切れ）
        old_tree_data = {"nodes": [], "edges": [], "metadata": {}}
        skill_tree = SkillTree(
            user_id=user.id,
            category=category.value,
            tree_data=old_tree_data,
            generated_at=datetime.now(UTC) - timedelta(minutes=15),
        )
        db.add(skill_tree)
        db.commit()

        # Mock: LLM呼び出しとGitHub API、settings
        new_tree_data = {
            "nodes": [
                {
                    "id": "ai_python_basics",
                    "name": "Python基礎",
                    "completed": True,
                    "description": "Python言語の基礎",
                    "prerequisites": [],
                    "estimated_hours": 30,
                }
            ],
            "edges": [],
            "metadata": {
                "total_nodes": 1,
                "completed_nodes": 1,
                "progress_percentage": 100.0,
                "next_recommended": ["ai_numpy"],
            },
        }

        with patch(
            "app.services.skill_tree_service.invoke_llm",
            new_callable=AsyncMock,
            return_value=json.dumps(new_tree_data),
        ), patch(
            "app.services.skill_tree_service.analyze_github_profile",
            new_callable=AsyncMock,
            return_value={
                "languages": ["Python"],
                "repo_count": 10,
                "tech_stack": ["FastAPI"],
                "recent_activity": "過去30日で10コミット",
                "completion_signals": {"ai_python_basics": True},
            },
        ), patch(
            "app.services.skill_tree_service.settings"
        ) as mock_settings:
            mock_settings.SKILL_TREE_CACHE_MINUTES = 10  # 15分前のキャッシュは無効
            mock_settings.SKIP_LLM_FOR_SKILL_TREE = False  # LLMを使用
            # Act: generate_skill_tree_ai を呼び出し
            result = await generate_skill_tree_ai(user.id, category, db)

        # Assert: 新しいデータが返却されることを確認
        assert result.category == category.value
        assert result.tree_data["nodes"][0]["id"] == "ai_python_basics"
        assert result.tree_data["nodes"][0]["completed"] is True

    @pytest.mark.asyncio
    async def test_generate_skill_tree_ai_with_github_data(self, db: Session):
        """GitHub分析結果がcompleted判定に反映される"""
        # Arrange
        category = SkillCategory.WEB

        # User→Profileを作成
        user = User(username="test_user", rank=6)
        db.add(user)
        db.flush()

        profile = Profile(
            user_id=user.id,
            github_username="octocat",
        )
        db.add(profile)
        db.commit()

        # Mock: GitHub APIで「JavaScript, TypeScript」を使用中
        github_analysis = {
            "languages": ["JavaScript", "TypeScript"],
            "repo_count": 25,
            "tech_stack": ["React", "Next.js"],
            "recent_activity": "過去30日で20コミット",
            "completion_signals": {
                "web_js_basics": True,
                "web_typescript": True,
                "web_react": True,
            },
        }

        llm_response = {
            "nodes": [
                {
                    "id": "web_js_basics",
                    "name": "JavaScript基礎",
                    "completed": True,
                    "description": "JavaScript言語の基礎",
                    "prerequisites": [],
                    "estimated_hours": 20,
                },
                {
                    "id": "web_react",
                    "name": "React",
                    "completed": True,
                    "description": "React フレームワーク",
                    "prerequisites": ["web_js_basics"],
                    "estimated_hours": 40,
                },
            ],
            "edges": [{"from": "web_js_basics", "to": "web_react"}],
            "metadata": {
                "total_nodes": 2,
                "completed_nodes": 2,
                "progress_percentage": 100.0,
                "next_recommended": ["web_nextjs"],
            },
        }

        with patch(
            "app.services.skill_tree_service.analyze_github_profile",
            new_callable=AsyncMock,
            return_value=github_analysis,
        ), patch(
            "app.services.skill_tree_service.invoke_llm",
            new_callable=AsyncMock,
            return_value=json.dumps(llm_response),
        ), patch(
            "app.core.config.settings.SKIP_LLM_FOR_SKILL_TREE",
            False,
        ):
            # Act
            result = await generate_skill_tree_ai(user.id, category, db)

        # Assert: completed=True が反映されている
        assert result.tree_data["nodes"][0]["completed"] is True
        assert result.tree_data["nodes"][1]["completed"] is True

    @pytest.mark.asyncio
    async def test_generate_skill_tree_ai_github_overrides_llm(self, db: Session):
        """LLMがcompletedをfalseで返してもGitHub分析結果が優先される"""
        # Arrange
        category = SkillCategory.WEB

        # Profileを作成
        user = User(username="test_user", rank=5)
        db.add(user)
        db.flush()

        profile = Profile(
            user_id=user.id,
            github_username="testuser",
        )
        db.add(profile)
        db.commit()

        # Mock: GitHub APIで「web_html_css」を習得済みと判定
        github_analysis = {
            "languages": ["HTML", "CSS", "JavaScript"],
            "repo_count": 10,
            "tech_stack": [],
            "recent_activity": "過去30日で5コミット",
            "completion_signals": {
                "web_html_css": True,  # ← GitHub分析で習得済み
            },
        }

        # LLMはcompletedをfalseで返す（間違った判定）
        llm_response = {
            "nodes": [
                {
                    "id": "web_html_css",
                    "name": "HTML/CSS基礎",
                    "completed": False,  # ← LLMは未習得と判定（誤り）
                    "description": "HTML/CSS基礎",
                    "prerequisites": [],
                    "estimated_hours": 15,
                },
                {
                    "id": "web_js_basics",
                    "name": "JavaScript基礎",
                    "completed": False,
                    "description": "JavaScript基礎",
                    "prerequisites": ["web_html_css"],
                    "estimated_hours": 20,
                },
            ],
            "edges": [{"from": "web_html_css", "to": "web_js_basics"}],
            "metadata": {
                "total_nodes": 2,
                "completed_nodes": 0,
                "progress_percentage": 0.0,
                "next_recommended": ["web_html_css"],
            },
        }

        with patch(
            "app.services.skill_tree_service.analyze_github_profile",
            new_callable=AsyncMock,
            return_value=github_analysis,
        ), patch(
            "app.services.skill_tree_service.invoke_llm",
            new_callable=AsyncMock,
            return_value=json.dumps(llm_response),
        ), patch(
            "app.core.config.settings.SKIP_LLM_FOR_SKILL_TREE",
            False,
        ):
            # Act
            result = await generate_skill_tree_ai(user.id, category, db)

        # Assert: GitHub分析結果が優先されてcompletedがtrueに上書きされる
        web_html_css_node = next(
            (n for n in result.tree_data["nodes"] if n["id"] == "web_html_css"), None
        )
        assert web_html_css_node is not None
        assert (
            web_html_css_node["completed"] is True
        )  # ← LLMのfalseがtrueに上書きされる

        # metadataも再計算されている
        assert result.tree_data["metadata"]["completed_nodes"] == 1
        assert result.tree_data["metadata"]["progress_percentage"] == 50.0

    @pytest.mark.asyncio
    async def test_generate_skill_tree_ai_user_not_found(self, db: Session):
        """ユーザーが存在しない場合は404エラー"""
        from fastapi import HTTPException

        user_id = 9999
        category = SkillCategory.SECURITY

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await generate_skill_tree_ai(user_id, category, db)

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_generate_skill_tree_ai_llm_failure_fallback(self, db: Session):
        """LLM呼び出し失敗時はベースラインJSONを返却"""
        # Arrange
        category = SkillCategory.INFRASTRUCTURE

        # User→Profileを作成
        user = User(username="test_user", rank=3)
        db.add(user)
        db.flush()

        profile = Profile(
            user_id=user.id,
            github_username="testuser",
        )
        db.add(profile)
        db.commit()

        # Mock: LLMが例外を投げる
        with patch(
            "app.services.skill_tree_service.analyze_github_profile",
            new_callable=AsyncMock,
            return_value={
                "languages": [],
                "repo_count": 0,
                "tech_stack": [],
                "recent_activity": "不明",
                "completion_signals": {},
            },
        ), patch(
            "app.services.skill_tree_service.invoke_llm",
            new_callable=AsyncMock,
            side_effect=Exception("LLM error"),
        ):
            # Act
            result = await generate_skill_tree_ai(user.id, category, db)

        # Assert: ベースラインJSONが返却される
        assert result.category == category.value
        assert "nodes" in result.tree_data
        assert len(result.tree_data["nodes"]) > 0  # ベースラインデータが存在

    def test_is_cache_valid_within_10_minutes(self):
        """settings.SKILL_TREE_CACHE_MINUTES以内のキャッシュは有効"""
        with patch("app.services.skill_tree_service.settings") as mock_settings:
            mock_settings.SKILL_TREE_CACHE_MINUTES = 10
            generated_at = datetime.now(UTC) - timedelta(minutes=5)
            assert _is_cache_valid(generated_at) is True

    def test_is_cache_valid_over_10_minutes(self):
        """settings.SKILL_TREE_CACHE_MINUTES以上前のキャッシュは無効"""
        with patch("app.services.skill_tree_service.settings") as mock_settings:
            mock_settings.SKILL_TREE_CACHE_MINUTES = 10
            generated_at = datetime.now(UTC) - timedelta(minutes=15)
            assert _is_cache_valid(generated_at) is False

    def test_is_cache_valid_none(self):
        """Noneの場合は無効"""
        assert _is_cache_valid(None) is False

    def test_load_baseline_json_success(self):
        """ベースラインJSON読み込み成功"""
        # Act
        data = _load_baseline_json(SkillCategory.WEB)

        # Assert
        assert "nodes" in data
        assert "edges" in data
        assert "metadata" in data
        assert len(data["nodes"]) > 0

    def test_load_baseline_json_all_categories(self):
        """全カテゴリのベースラインJSON読み込み"""
        for category in SkillCategory:
            data = _load_baseline_json(category)
            assert "nodes" in data
            assert len(data["nodes"]) > 0

    def test_build_skill_tree_prompt(self):
        """LLMプロンプト生成のテスト"""
        # Arrange
        profile = MagicMock()
        profile.user = MagicMock()
        profile.user.rank = 4
        profile.github_username = "testuser"

        github_analysis = {
            "languages": ["Python", "JavaScript"],
            "repo_count": 15,
            "tech_stack": ["FastAPI", "React"],
            "recent_activity": "過去30日で10コミット",
            "completion_signals": {"web_js_basics": True},
        }

        completed_quests = ["HTML基礎演習", "JavaScript基礎演習"]

        baseline_data = {
            "nodes": [{"id": "test", "name": "Test"}],
            "edges": [],
            "metadata": {},
        }

        # Act
        prompt = _build_skill_tree_prompt(
            profile=profile,
            category=SkillCategory.WEB,
            github_analysis=github_analysis,
            completed_quests=completed_quests,
            baseline_data=baseline_data,
        )

        # Assert: プロンプトに必要な情報が含まれているか
        assert "testuser" in prompt
        assert "FastAPI" in prompt  # tech_stackが含まれている
        assert "React" in prompt  # tech_stackが含まれている
        assert "web_js_basics" in prompt  # completion_signalsが含まれている
        assert "母樹" in prompt  # rank 4 = 母樹
