
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CurrentUserResponse(BaseModel):
    id: UUID
    name: str | None
    email: str
    role_id: UUID
    role: str
    contact: str | None = None
    location: str | None = None
    status: str
    is_active: bool
    last_login_at: datetime | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ProfileUpdateRequest(BaseModel):
    """Fields a user may change on their own profile (email and role are managed by admins)."""

    name: str | None = Field(default=None, max_length=100)
    contact: str | None = Field(default=None, max_length=20, description="phone number")
    location: str | None = Field(default=None, max_length=100)

    @field_validator("name", "contact", "location", mode="before")
    @classmethod
    def blank_to_none(cls, value):
        if isinstance(value, str):
            value = " ".join(value.split())
            return value or None
        return value

    @field_validator("contact")
    @classmethod
    def phone_like(cls, value):
        if value is not None:
            digits = sum(c.isdigit() for c in value)
            if digits < 7 or any(c not in "0123456789+-() " for c in value):
                raise ValueError("Enter a valid phone number.")
        return value
