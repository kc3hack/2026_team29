from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    pass


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
