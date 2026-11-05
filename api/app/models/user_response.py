import uuid
from datetime import datetime
from pydantic import BaseModel


class UserResponse(BaseModel):
    id: uuid.UUID
    first_name: str | None
    last_name: str | None
    created_at: datetime
