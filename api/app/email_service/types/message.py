from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel
from pydantic import ConfigDict

class EmailMessage(BaseModel):
    id: str
    sender: str
    cc: str | None = None
    bcc: str | None = None
    subject: str | None = None
    labels: list[str] = []
    text: str | None = None
    received_at: datetime | None = None
    thread_id: str
