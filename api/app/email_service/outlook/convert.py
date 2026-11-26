from dataclasses import dataclass
from email.utils import formataddr

from app.email_service.outlook.types.message import Message
from app.email_service.outlook.types.message import Recipient
from app.email_service.types.message import EmailMessage
from app.email_service.types.message import MessageLabel
from app.email_service.types.thread import EmailThread


@dataclass(frozen=True)
class OutlookFolderIds:
    sent: str | None = None
    junk: str | None = None
    deleted: str | None = None


def to_email_message(message: Message, folders: OutlookFolderIds) -> EmailMessage:
    headers = {header.name.lower(): header.value for header in message.internetMessageHeaders}

    if message.from_user is not None and "from" not in headers:
        headers["from"] = format_recipient(message.from_user)
    if message.subject is not None:
        headers.setdefault("subject", message.subject)
    if message.replyTo and "reply-to" not in headers:
        headers["reply-to"] = ", ".join(format_recipient(recipient) for recipient in message.replyTo)
    if message.internetMessageId:
        headers.setdefault("message-id", message.internetMessageId)

    return EmailMessage(
        id=message.id,
        thread_id=message.conversationId or message.id,
        headers=headers,
        text=message.text,
        received_at=message.receivedDateTime,
        labels=_labels(message, folders),
    )


def to_email_thread(thread_id: str, messages: list[Message], folders: OutlookFolderIds) -> EmailThread:
    return EmailThread(id=thread_id, messages=[to_email_message(message, folders) for message in messages])


def format_recipient(recipient: Recipient) -> str:
    address = recipient.emailAddress
    return formataddr((address.name or "", address.address or ""))


def _labels(message: Message, folders: OutlookFolderIds) -> frozenset[MessageLabel]:
    labels: set[MessageLabel] = set()
    if message.isDraft:
        labels.add(MessageLabel.DRAFT)

    folder = message.parentFolderId
    if folder is not None:
        if folder == folders.sent:
            labels.add(MessageLabel.SENT)
        elif folder == folders.junk:
            labels.add(MessageLabel.SPAM)
        elif folder == folders.deleted:
            labels.add(MessageLabel.TRASH)

    return frozenset(labels)
