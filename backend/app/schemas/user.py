from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    pass


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
