import uuid
from datetime import datetime
from pydantic import BaseModel
from pydantic import ConfigDict

from app.db.schema import DraftStatus


class DraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email_account_id: uuid.UUID
    reply_to_email: uuid.UUID | None = None
    to_address: str
    subject: str | None = None
    body: str | None = None
    status: DraftStatus
    created_at: datetime
    updated_at: datetime
