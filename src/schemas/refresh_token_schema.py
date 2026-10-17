
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RefreshTokenRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    exp_at: datetime
    last_used_at: datetime | None = None
    created_at: datetime | None = None
    revoked_at: datetime | None = None
