"""Profile スキーマのバリデーションテスト"""

import pytest
from pydantic import ValidationError

from app.schemas.profile import ProfileCreate


def test_profile_create_valid_url():
    """正しいURL形式は受け入れられる"""
    profile = ProfileCreate(
        user_id=1,
        portfolio_url="https://example.com/portfolio",
    )
    assert str(profile.portfolio_url) == "https://example.com/portfolio"


def test_profile_create_invalid_url():
    """不正なURL形式はValidationError"""
    with pytest.raises(ValidationError) as exc_info:
        ProfileCreate(
            user_id=1,
            portfolio_url="not-a-url",
        )
    assert "URL" in str(exc_info.value)


def test_profile_create_url_none():
    """portfolio_urlがNoneでも作成できる"""
    profile = ProfileCreate(user_id=1)
    assert profile.portfolio_url is None
