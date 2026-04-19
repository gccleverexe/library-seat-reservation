from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RegisterRequest(BaseModel):
    campus_id: str = Field(min_length=1)
    password: str = Field(min_length=6)
    name: str = Field(min_length=1)


class LoginRequest(BaseModel):
    campus_id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    id: int
    campus_id: str
    name: str
    role: str
    is_restricted: bool
    restricted_until: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
