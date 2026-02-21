from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str | None = None  # ID入力ログイン用。GitHub OAuth経由の作成時はNone

    @field_validator("password")
    @classmethod
    def password_must_not_be_empty(cls, v: str | None) -> str | None:
        if v is not None:
            if not v.strip():
                raise ValueError("password must not be empty string")
            if len(v) > 128:
                raise ValueError("password must be at most 128 characters")
        return v


class UserUpdate(BaseModel):
    """PUT /users/{user_id} のリクエストボディ。
    username のみユーザーが変更可能。
    rank は AI 専用 CRUD (update_user_rank) で管理。
    exp / level はサーバー側で管理。
    詳細は ADR 010, 011 参照。
    """

    username: str | None = None


class User(UserBase):
    id: int
    level: int
    exp: int
    rank: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
