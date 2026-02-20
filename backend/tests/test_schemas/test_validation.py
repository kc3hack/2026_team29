"""Pydanticスキーマバリデーションテスト（統合版）"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models.enums import BadgeCategory, QuestCategory
from app.schemas.badge import BadgeCreate
from app.schemas.oauth_account import OAuthAccountCreate
from app.schemas.profile import ProfileCreate
from app.schemas.quest import QuestCreate
from app.schemas.user import User


def test_badge_tier_validation():
    """Badge.tier: 1-3は正常、範囲外はエラー"""
    BadgeCreate(user_id=1, category=BadgeCategory.COMMIT, tier=1)
    BadgeCreate(user_id=1, category=BadgeCategory.COMMIT, tier=3)

    with pytest.raises(ValidationError):
        BadgeCreate(user_id=1, category=BadgeCategory.COMMIT, tier=0)
    with pytest.raises(ValidationError):
        BadgeCreate(user_id=1, category=BadgeCategory.COMMIT, tier=4)


def test_quest_difficulty_validation():
    """Quest.difficulty: 0-9は正常、範囲外はエラー"""
    QuestCreate(title="T", description="d", difficulty=0, category=QuestCategory.WEB)
    QuestCreate(title="T", description="d", difficulty=9, category=QuestCategory.WEB)

    with pytest.raises(ValidationError):
        QuestCreate(
            title="T", description="d", difficulty=-1, category=QuestCategory.WEB
        )
    with pytest.raises(ValidationError):
        QuestCreate(
            title="T", description="d", difficulty=10, category=QuestCategory.WEB
        )


def test_oauth_provider_validation():
    """OAuthAccount.provider: githubは正常、未許可providerはエラー"""
    OAuthAccountCreate(
        user_id=1, provider="github", provider_user_id="123", access_token="token"
    )

    with pytest.raises(ValidationError):
        OAuthAccountCreate(
            user_id=1, provider="twitter", provider_user_id="123", access_token="token"
        )


def test_profile_url_validation():
    """Profile.portfolio_url: 正しいURL形式のみ許可"""
    ProfileCreate(user_id=1, portfolio_url="https://example.com")
    ProfileCreate(user_id=1)  # Noneも許可

    with pytest.raises(ValidationError):
        ProfileCreate(user_id=1, portfolio_url="not-a-url")


def test_user_rank_is_ai_managed():
    """User.rank: AIが自由に設定可能（exp との整合性チェックなし）。ADR 010 参照。"""
    now = datetime.now(timezone.utc)

    # exp=0 でも rank=1 はAI判定として有効
    User(
        id=1,
        username="test",
        level=1,
        exp=0,
        rank=1,
        created_at=now,
        updated_at=now,
    )

    # exp=0 で rank=9 (最高ランク) もAI判定として有効
    User(
        id=2,
        username="test2",
        level=1,
        exp=0,
        rank=9,
        created_at=now,
        updated_at=now,
    )
