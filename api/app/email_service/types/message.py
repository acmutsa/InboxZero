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
    labels : [str] = []
    text: str | None = None
    received_at: datetime | None = None
    thread_id: str
    # is_draft: bool = False
    # is_unread: bool = False
    # is_sent: bool | None = None
    # is_spam: bool | None = None
    # is_trash: bool | None = None
