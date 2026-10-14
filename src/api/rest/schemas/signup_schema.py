
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    contact: str | None = Field(default=None, max_length=30)
    location: str | None = Field(default=None, max_length=150)


class SignupResponse(BaseModel):
    message: str = "Account created successfully."
