from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel
from pydantic import ConfigDict


class MessageLabel(StrEnum):
    SENT = "SENT"              
    DRAFT = "DRAFT"
    SPAM = "SPAM"
    TRASH = "TRASH"
    PROMOTIONS = "PROMOTIONS"
    SOCIAL = "SOCIAL"
    FORUMS = "FORUMS"


class EmailMessage(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    thread_id: str
    headers: dict[str, str] = {}
    text: str | None = None
    received_at: datetime | None = None
    labels: frozenset[MessageLabel] = frozenset()

    def header(self, name: str) -> str | None:
        return self.headers.get(name.lower())

    @property
    def sender(self) -> str | None:
        return self.header("from")

    @property
    def subject(self) -> str | None:
        return self.header("subject")

    @property
    def is_sent(self) -> bool:
        return MessageLabel.SENT in self.labels

    @property
    def is_draft(self) -> bool:
        return MessageLabel.DRAFT in self.labels

    @property
    def reply_references(self) -> list[str]:
        references = (self.header("references") or "").split()
        message_id = self.header("message-id")
        if message_id and message_id not in references:
            references.append(message_id)
        return references
