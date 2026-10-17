
from pydantic import BaseModel


class RefreshResponse(BaseModel):
    message: str = "Access token refreshed successfully."
