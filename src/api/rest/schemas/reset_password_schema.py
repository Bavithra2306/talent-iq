
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, StringConstraints

OTP = Annotated[
    str,
    StringConstraints(pattern=r"^[0-9]{6}$"),
]


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: OTP
    new_password: str = Field(min_length=8, max_length=128)


class ResetPasswordResponse(BaseModel):
    message: str = (
        "Password reset successfully. Please log in again."
    )
