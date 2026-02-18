"""Profile スキーマ"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProfileCreate(BaseModel):
    user_id: int
    github_username: str | None = None
    qiita_id: str | None = None
    connpass_id: str | None = None
    portfolio_url: str | None = None
    portfolio_text: str | None = None


class ProfileUpdate(BaseModel):
    github_username: str | None = None
    qiita_id: str | None = None
    connpass_id: str | None = None
    portfolio_url: str | None = None
    portfolio_text: str | None = None


class Profile(BaseModel):
    id: int
    user_id: int
    github_username: str | None
    qiita_id: str | None
    connpass_id: str | None
    portfolio_url: str | None
    portfolio_text: str | None
    last_analyzed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
