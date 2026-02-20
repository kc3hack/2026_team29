from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


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

    @model_validator(mode="after")
    def validate_rank_consistency(self) -> "User":
        """経験値とランクの整合性を検証する"""
        from app.core.rank import calculate_rank

        expected_rank = calculate_rank(self.exp)
        if self.rank != expected_rank:
            raise ValueError(
                f"Rank inconsistency: exp={self.exp} should yield rank={expected_rank}, but got rank={self.rank}"
            )
        return self
