
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class InvitationRequest(BaseModel):
    email: EmailStr
    role: Literal["recruiter", "hiring_manager"]


class InvitationResponse(BaseModel):
    message: str


class AcceptInvitationRequest(BaseModel):
    token: str = Field(min_length=20)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)


class AcceptInvitationResponse(BaseModel):
    message: str
