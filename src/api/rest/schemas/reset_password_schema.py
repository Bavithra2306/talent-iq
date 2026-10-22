
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, StringConstraints, field_validator

from src.core.services.password_policy import check_new_password

OTP = Annotated[
    str,
    StringConstraints(pattern=r"^[0-9]{6}$"),
]


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: OTP
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def strong_password(cls, value: str) -> str:
        return check_new_password(value)


class ResetPasswordResponse(BaseModel):
    message: str = (
        "Password reset successfully. Please log in again."
    )
