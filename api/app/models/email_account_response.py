import uuid
from datetime import datetime
from pydantic import BaseModel

from app.db.schema import EmailServiceProvider


class EmailAccountResponse(BaseModel):
    id: uuid.UUID
    email_account: str
    provider: EmailServiceProvider
    created_at: datetime
