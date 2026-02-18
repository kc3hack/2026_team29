"""OAuthAccount スキーマ"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OAuthAccountCreate(BaseModel):
    user_id: int
    provider: str
    provider_user_id: str
    access_token: str  # 平文で受け取り、CRUD層で暗号化
    refresh_token: str | None = None
    expires_at: datetime | None = None


class OAuthTokenUpdate(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    expires_at: datetime | None = None


class OAuthAccount(BaseModel):
    """レスポンス用（トークン値は含めない）"""

    id: int
    user_id: int
    provider: str
    provider_user_id: str
    expires_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
