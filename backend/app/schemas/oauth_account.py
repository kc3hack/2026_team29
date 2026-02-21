"""OAuthAccount スキーマ"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

# MVP段階で対応するOAuthプロバイダ（将来拡張可能）
ALLOWED_PROVIDERS = {"github"}


class OAuthAccountCreate(BaseModel):
    user_id: int
    provider: str
    provider_user_id: str
    access_token: str  # 平文で受け取り、CRUD層で暗号化
    refresh_token: str | None = None
    expires_at: datetime | None = None

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        if v not in ALLOWED_PROVIDERS:
            raise ValueError(f"provider must be one of {ALLOWED_PROVIDERS}")
        return v


class OAuthTokenUpdate(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    expires_at: datetime | None = None

    @field_validator("access_token", "refresh_token")
    @classmethod
    def token_must_not_be_empty(cls, v: str | None) -> str | None:
        """C-5: 空文字トークンの暗号化保存を防ぐ。"""
        if v is not None and not v.strip():
            raise ValueError("token must not be empty string")
        return v


class OAuthAccount(BaseModel):
    """レスポンス用（トークン値は含めない）"""

    id: int
    user_id: int
    provider: str
    provider_user_id: str
    expires_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
