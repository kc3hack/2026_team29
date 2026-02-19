"""Quest スキーマのバリデーションテスト"""

import pytest
from pydantic import ValidationError

from app.models.enums import QuestCategory
from app.schemas.quest import QuestCreate


def test_quest_create_valid_difficulty():
    """difficulty 0-9 は正常に作成できる"""
    for difficulty in range(10):
        quest = QuestCreate(
            title="Test",
            description="desc",
            difficulty=difficulty,
            category=QuestCategory.WEB,
        )
        assert quest.difficulty == difficulty


def test_quest_create_invalid_difficulty_negative():
    """difficulty -1はValidationError"""
    with pytest.raises(ValidationError) as exc_info:
        QuestCreate(
            title="Test",
            description="desc",
            difficulty=-1,
            category=QuestCategory.WEB,
        )
    assert "difficulty must be 0-9" in str(exc_info.value)


def test_quest_create_invalid_difficulty_too_high():
    """difficulty 10以上はValidationError"""
    with pytest.raises(ValidationError) as exc_info:
        QuestCreate(
            title="Test",
            description="desc",
            difficulty=10,
            category=QuestCategory.WEB,
        )
    assert "difficulty must be 0-9" in str(exc_info.value)
