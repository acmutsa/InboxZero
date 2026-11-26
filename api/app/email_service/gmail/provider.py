from app.email_service.gmail.convert import to_reply_draft_request
from app.db.schema import EmailAccount
from app.email_service.gmail.convert import to_email_message
from app.email_service.gmail.convert import to_email_thread
from app.email_service.gmail.gmail import GmailService
from app.email_service.gmail.token_manager import GmailTokenManager
from app.email_service.gmail.types.error import GmailServiceError
from app.email_service.gmail.types.label import LablelCreateRequest
from app.email_service.gmail.types.message_modify_request import MessageModifyRequest
from app.email_service.gmail.types.message_request import MessageRequest
from app.email_service.gmail.types.thread import ThreadRequest
from app.email_service.provider import EmailProvider
from app.email_service.types.draft import ReplyDraft
from app.email_service.types.message import EmailMessage
from app.email_service.types.thread import EmailThread


CATEGORY_LABEL_PREFIX = "InboxZero/"


class GmailProvider(EmailProvider):
    def __init__(self, account: EmailAccount) -> None:
        self._gmail = GmailService(GmailTokenManager(account))

    def get_message(self, message_id: str) -> EmailMessage:
        return to_email_message(self._gmail.get_message(MessageRequest(id=message_id)))

    def get_thread(self, thread_id: str) -> EmailThread:
        return to_email_thread(self._gmail.get_thread(ThreadRequest(id=thread_id, format="metadata")))

    def create_reply_draft(self, original: EmailMessage, reply: ReplyDraft) -> str:
        request = to_reply_draft_request(
            to_address=reply.to_address,
            subject=reply.subject,
            body=reply.body,
            thread_id=original.thread_id,
            in_reply_to=original.header("message-id"),
            references=original.reply_references,
        )
        return self._gmail.post_draft(request).id

    def apply_category(self, message_id: str, category_name: str) -> None:
        label_id = self._category_label_id(f"{CATEGORY_LABEL_PREFIX}{category_name}")
        self._gmail.modify_message(MessageModifyRequest(id=message_id, addLabelIds=[label_id]))

    def _category_label_id(self, label_name: str) -> str:
        label_id = self._find_label_id(label_name)
        if label_id is not None:
            return label_id
        try:
            return self._gmail.post_label(LablelCreateRequest(name=label_name)).id
        except GmailServiceError as error:
            label_id = self._find_label_id(label_name) if error.status_code == 409 else None
            if label_id is None:
                raise
            return label_id

    def _find_label_id(self, label_name: str) -> str | None:
        wanted = label_name.lower()
        return next((label.id for label in self._gmail.get_labels() if label.name.lower() == wanted), None)
