from pydantic import BaseModel
from pydantic import ConfigDict

from app.email_service.types.message import EmailMessage


class EmailThread(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    messages: list[EmailMessage] = []

    def is_reply(self, message: EmailMessage) -> bool:
        has_reply_headers = message.header("In-Reply-To") or message.header("References")
        return bool(has_reply_headers or self._older_than(message))

    def already_replied(self, message: EmailMessage) -> bool:
        return any(m.is_sent for m in self._newer_than(message))

    def is_latest(self, message: EmailMessage) -> bool:
        return not self._newer_than(message)

    def previous_message_id(self, message: EmailMessage) -> str | None:
        older = self._older_than(message)
        if not older:
            return None
        return max(older, key=lambda m: m.received_at).id

    def skip_reason(self, message: EmailMessage) -> str | None:
        if self.already_replied(message):
            return "already replied in thread"
        if not self.is_latest(message):
            return "newer message in thread"
        return None

    def _conversation_messages(self, message: EmailMessage) -> list[EmailMessage]:
        return [m for m in self.messages if m.id != message.id and not m.is_draft]

    def _older_than(self, message: EmailMessage) -> list[EmailMessage]:
        return [m for m in self._conversation_messages(message) if _is_newer(message, than=m)]

    def _newer_than(self, message: EmailMessage) -> list[EmailMessage]:
        return [m for m in self._conversation_messages(message) if _is_newer(m, than=message)]


def _is_newer(message: EmailMessage, than: EmailMessage) -> bool:
    if message.received_at is None or than.received_at is None:
        return False
    return message.received_at > than.received_at
