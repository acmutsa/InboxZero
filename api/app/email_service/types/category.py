from enum import StrEnum

from pydantic import BaseModel
from pydantic import ConfigDict

class EmailCategory(BaseModel):
    id: str
    name: str
    parent_id: str | None = None    # Outlook folders nest by parent id; Gmail nests by name ("InboxZero/Work")
    is_system: bool = False         # Gmail INBOX, SENT, SPAM...; user-created categories are False
