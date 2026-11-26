import base64

from app.email_service.gmail.types.message import Message
from app.email_service.gmail.types.thread import Thread
from app.email_service.types.message import EmailMessage
from app.email_service.types.message import MessageLabel
from app.email_service.types.thread import EmailThread
from app.email_service.gmail.types.draft import DraftCreateRequest

GMAIL_LABELS: dict[str, MessageLabel] = {
    "SENT": MessageLabel.SENT,
    "DRAFT": MessageLabel.DRAFT,
    "SPAM": MessageLabel.SPAM,
    "TRASH": MessageLabel.TRASH,
    "CATEGORY_PROMOTIONS": MessageLabel.PROMOTIONS,
    "CATEGORY_SOCIAL": MessageLabel.SOCIAL,
    "CATEGORY_FORUMS": MessageLabel.FORUMS,
}


def to_email_message(message: Message) -> EmailMessage:
    headers = {header.name.lower(): header.value for header in message.payload.headers} if message.payload else {}
    return EmailMessage(
        id=message.id,
        thread_id=message.threadId or message.id,
        headers=headers,
        text=message.text,
        received_at=message.received_at,
        labels=frozenset(GMAIL_LABELS[label] for label in message.labelIds if label in GMAIL_LABELS),
    )


def to_email_thread(thread: Thread) -> EmailThread:
    return EmailThread(id=thread.id, messages=[to_email_message(message) for message in thread.messages])

def to_reply_draft_request(
    to_address: str,
    subject: str,
    body: str,
    thread_id: str | None,
    in_reply_to: str | None,
    references: list[str],
) -> DraftCreateRequest:

    message = EmailMessage()
    message["To"] = to_address
    message["Subject"] = subject
    if in_reply_to:
        message["In-Reply-To"] = in_reply_to
    if references:
        message["References"] = " ".join(references)
    message.set_content(body)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")
    return DraftCreateRequest(message=DraftMessage(raw=raw, threadId=thread_id))