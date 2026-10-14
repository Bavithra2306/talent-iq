
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    contact: str | None = Field(default=None, max_length=30)
    location: str | None = Field(default=None, max_length=150)
    role_id: UUID
    password_hash: str


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    contact: str | None = Field(default=None, max_length=30)
    location: str | None = Field(default=None, max_length=150)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: EmailStr
    contact: str | None = None
    location: str | None = None
    role_id: UUID
    is_active: bool
    last_login_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
