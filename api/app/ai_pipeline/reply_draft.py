
import base64

from email.message import EmailMessage

from app.email_service.gmail.types.draft import DraftCreateRequest
from app.email_service.gmail.types.draft import DraftMessage


def build_reply_draft_request(
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
