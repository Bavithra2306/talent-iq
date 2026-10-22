
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from src.core.services.password_policy import check_new_password


class InvitationRequest(BaseModel):
    email: EmailStr
    role: Literal["recruiter", "hiring_manager"]


class InvitationResponse(BaseModel):
    message: str


class AcceptInvitationRequest(BaseModel):
    token: str = Field(min_length=20)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def strong_password(cls, value: str) -> str:
        return check_new_password(value)

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Password and confirmation do not match.")
        return self


class AcceptInvitationResponse(BaseModel):
    message: str
