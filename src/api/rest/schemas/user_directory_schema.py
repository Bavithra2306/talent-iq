
from uuid import UUID

from pydantic import BaseModel


class DirectoryUser(BaseModel):
    id: UUID
    name: str | None
    email: str
    role: str
    status: str
    blocked: bool = False
