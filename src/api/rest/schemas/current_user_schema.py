
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CurrentUserResponse(BaseModel):
    id: UUID
    name: str | None
    email: str
    role_id: UUID
    status: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
