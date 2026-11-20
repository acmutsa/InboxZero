"""Thread facts for the pipeline, worked out from the Gmail message and its thread.

Nothing here is stored in the database. `process_email` fetches the message and
its thread from Gmail, builds a ThreadContext (and the previous message, if
any), and puts them into the pipeline state.
"""

import re

from pydantic import BaseModel
from pydantic import ConfigDict

from app.email_service.gmail.types.message import Message
from app.email_service.gmail.types.thread import Thread


class ThreadContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    thread_id: str
    # Messages in the thread, not counting drafts.
    message_count: int
    # The email answers an earlier one: it has reply headers, or an older
    # message exists in its thread.
    is_reply: bool
    # The user sent a message in this thread after this email arrived.
    already_replied: bool
    # No newer message (other than drafts) exists in the thread.
    is_latest_in_thread: bool
    # This email's Message-ID header. A reply sets In-Reply-To to this value.
    message_id_header: str | None
    # The References header a reply to this email should carry.
    reply_references: list[str]
    # Gmail id of the message just before this one in the thread, if any.
    previous_message_id: str | None = None


class PreviousMessage(BaseModel):
    """The message just before the email in its thread, as context for the LLM."""

    model_config = ConfigDict(frozen=True)

    from_address: str
    # True when the user sent it (it has the SENT label).
    sent_by_user: bool
    # Body with quoted earlier history removed, cut to a maximum length.
    text: str


def build_thread_context(message: Message, thread: Thread) -> ThreadContext:
    others = _conversation_messages(message, thread)
    newer = [m for m in others if _is_newer(m, than=message)]
    older = [m for m in others if _is_newer(message, than=m)]

    message_id_header = message.header("Message-ID")
    in_reply_to = message.header("In-Reply-To")
    references = (message.header("References") or "").split()

    reply_references = list(references)
    if message_id_header and message_id_header not in reply_references:
        reply_references.append(message_id_header)

    return ThreadContext(
        thread_id=thread.id,
        message_count=len(others) + 1,
        is_reply=bool(in_reply_to or references or older),
        already_replied=any("SENT" in m.labelIds for m in newer),
        is_latest_in_thread=not newer,
        message_id_header=message_id_header,
        reply_references=reply_references,
        previous_message_id=find_previous_message_id(message, thread),
    )


def find_previous_message_id(message: Message, thread: Thread) -> str | None:
    """Id of the newest message older than `message` in the thread, drafts excluded."""
    older = [m for m in _conversation_messages(message, thread) if _is_newer(message, than=m)]
    if not older:
        return None
    return max(older, key=lambda m: int(m.internalDate or 0)).id


def build_previous_message(message: Message, max_chars: int) -> PreviousMessage:
    return PreviousMessage(
        from_address=message.sender or "(unknown sender)",
        sent_by_user="SENT" in message.labelIds,
        text=truncate(strip_quoted_reply(message.text or ""), max_chars),
    )


def thread_skip_reason(thread: ThreadContext) -> str | None:
    """Gate 1 thread checks. Return why to skip, or None to continue."""
    if thread.already_replied:
        return "already replied in thread"
    if not thread.is_latest_in_thread:
        # The newer message gets its own pipeline run.
        return "newer message in thread"
    return None


# Where quoted history starts in a reply. Mail clients put the earlier
# messages below one of these lines.
_QUOTE_STARTS = (
    # Gmail / Apple Mail: "On Tue, Nov 3, 2026 at 2:00 PM Jane <jane@x.com> wrote:".
    # Gmail wraps long ones, so allow it to run over a couple of lines.
    re.compile(r"^On (?:[^\n]*\n){0,2}?[^\n]*wrote:[ \t]*$", re.MULTILINE),
    # Outlook
    re.compile(r"^-{2,}\s*Original Message\s*-{2,}", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^_{10,}[ \t]*\nFrom: ", re.MULTILINE),
)


def strip_quoted_reply(text: str) -> str:
    """Remove the quoted earlier messages a reply carries below its own text."""
    # Gmail's text/plain parts often use CRLF line endings.
    text = text.replace("\r\n", "\n")
    cut = min((m.start() for pattern in _QUOTE_STARTS if (m := pattern.search(text))), default=len(text))
    own_text = text[:cut]
    # Drop any remaining "> quoted" lines.
    lines = [line for line in own_text.splitlines() if not line.lstrip().startswith(">")]
    return "\n".join(lines).strip()


def truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n[... truncated]"


def _conversation_messages(message: Message, thread: Thread) -> list[Message]:
    # Drafts sit in the thread too (including ones this app creates), but they
    # are not part of the conversation yet.
    return [m for m in thread.messages if m.id != message.id and "DRAFT" not in m.labelIds]


def _is_newer(message: Message, than: Message) -> bool:
    # internalDate is when Gmail received the message, in epoch milliseconds.
    # Without both dates there is nothing to compare, so assume it is not newer.
    if message.internalDate is None or than.internalDate is None:
        return False
    return int(message.internalDate) > int(than.internalDate)
