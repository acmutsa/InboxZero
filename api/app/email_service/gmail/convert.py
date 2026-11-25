from app.email_service.gmail.types.message import Message
from app.email_service.gmail.types.thread import Thread
from app.email_service.types.message import EmailMessage
from app.email_service.types.message import MessageLabel
from app.email_service.types.message import EmailThread

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
