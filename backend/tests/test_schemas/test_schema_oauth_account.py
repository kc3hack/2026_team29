"""OAuthAccount スキーマのバリデーションテスト"""

import pytest
from pydantic import ValidationError

from app.schemas.oauth_account import OAuthAccountCreate


def test_oauth_account_create_valid_provider():
    """許可されたprovider（github）は正常に作成できる"""
    account = OAuthAccountCreate(
        user_id=1,
        provider="github",
        provider_user_id="12345",
        access_token="token",
    )
    assert account.provider == "github"


def test_oauth_account_create_invalid_provider():
    """許可されていないproviderはValidationError"""
    with pytest.raises(ValidationError) as exc_info:
        OAuthAccountCreate(
            user_id=1,
            provider="twitter",
            provider_user_id="12345",
            access_token="token",
        )
    assert "provider must be one of" in str(exc_info.value)
