from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    level: int
    exp: int
    rank: int
    skills: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
