"""Badge スキーマのバリデーションテスト"""

import pytest
from pydantic import ValidationError

from app.models.enums import BadgeCategory
from app.schemas.badge import BadgeCreate


def test_badge_create_valid_tier():
    """tier 1-3 は正常に作成できる"""
    for tier in [1, 2, 3]:
        badge = BadgeCreate(user_id=1, category=BadgeCategory.COMMIT, tier=tier)
        assert badge.tier == tier


def test_badge_create_invalid_tier_too_low():
    """tier 0以下はValidationError"""
    with pytest.raises(ValidationError) as exc_info:
        BadgeCreate(user_id=1, category=BadgeCategory.COMMIT, tier=0)
    assert "tier must be 1" in str(exc_info.value)


def test_badge_create_invalid_tier_too_high():
    """tier 4以上はValidationError"""
    with pytest.raises(ValidationError) as exc_info:
        BadgeCreate(user_id=1, category=BadgeCategory.COMMIT, tier=4)
    assert "tier must be 1" in str(exc_info.value)
