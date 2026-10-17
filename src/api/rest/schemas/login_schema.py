
from pydantic import BaseModel, EmailStr, Field

from src.schemas.user_schema import UserRead


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class LoginResponse(BaseModel):
    message: str = "Login successful."

