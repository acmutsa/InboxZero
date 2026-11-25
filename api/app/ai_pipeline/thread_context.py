import re

from pydantic import BaseModel
from pydantic import ConfigDict

from app.email_service.types.message import EmailMessage
from app.email_service.types.message import EmailThread


class ThreadContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    thread_id: str
    message_count: int
    is_reply: bool
    already_replied: bool
    is_latest_in_thread: bool
    message_id_header: str | None
    reply_references: list[str]
    previous_message_id: str | None = None


class PreviousMessage(BaseModel):
    model_config = ConfigDict(frozen=True)

    from_address: str

    sent_by_user: bool
    text: str


def build_thread_context(message: EmailMessage, thread: EmailThread) -> ThreadContext:
    others = _conversation_messages(message, thread)
    newer = [m for m in others if _is_newer(m, than=message)]
    older = [m for m in others if _is_newer(message, than=m)]

    in_reply_to = message.header("In-Reply-To")
    references = (message.header("References") or "").split()

    return ThreadContext(
        thread_id=thread.id,
        message_count=len(others) + 1,
        is_reply=bool(in_reply_to or references or older),
        already_replied=any(m.is_sent for m in newer),
        is_latest_in_thread=not newer,
        message_id_header=message.header("Message-ID"),
        reply_references=message.reply_references,
        previous_message_id=find_previous_message_id(message, thread),
    )


def find_previous_message_id(message: EmailMessage, thread: EmailThread) -> str | None:
    older = [m for m in _conversation_messages(message, thread) if _is_newer(message, than=m)]
    if not older:
        return None
    return max(older, key=lambda m: m.received_at).id


def build_previous_message(message: EmailMessage, max_chars: int) -> PreviousMessage:
    return PreviousMessage(
        from_address=message.sender or "(unknown sender)",
        sent_by_user=message.is_sent,
        text=truncate(strip_quoted_reply(message.text or ""), max_chars),
    )


def thread_skip_reason(thread: ThreadContext) -> str | None:
    if thread.already_replied:
        return "already replied in thread"
    if not thread.is_latest_in_thread:
        return "newer message in thread"
    return None


_QUOTE_STARTS = (

    re.compile(r"^On (?:[^\n]*\n){0,2}?[^\n]*wrote:[ \t]*$", re.MULTILINE),
    re.compile(r"^-{2,}\s*Original Message\s*-{2,}", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^_{10,}[ \t]*\nFrom: ", re.MULTILINE),
)


def strip_quoted_reply(text: str) -> str:
    text = text.replace("\r\n", "\n")
    cut = min((m.start() for pattern in _QUOTE_STARTS if (m := pattern.search(text))), default=len(text))
    own_text = text[:cut]
    lines = [line for line in own_text.splitlines() if not line.lstrip().startswith(">")]
    return "\n".join(lines).strip()


def truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n[... truncated]"


def _conversation_messages(message: EmailMessage, thread: EmailThread) -> list[EmailMessage]:
    return [m for m in thread.messages if m.id != message.id and not m.is_draft]


def _is_newer(message: EmailMessage, than: EmailMessage) -> bool:
    if message.received_at is None or than.received_at is None:
        return False
    return message.received_at > than.received_at
