from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    level: int
    exp: int
    rank: int
    skills: Optional[list[str]] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)