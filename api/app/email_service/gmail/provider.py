from app.db.schema import EmailAccount

from app.email_service.gmail.gmail import GmailService
from app.email_service.gmail.token_manager import GmailTokenManager
from app.email_service.gmail.types.draft import DraftCreateRequest
from app.email_service.gmail.types.label import LabelCreateRequest
from app.email_service.gmail.types.message_modify_request import MessageModifyRequest
from app.email_service.gmail.types.message_request import MessageRequest
from app.email_service.gmail.types.thread import ThreadRequest

from app.email_service.provider import EmailProvider
from app.email_service.types.category import EmailCategory
from app.email_service.types.category import EmailCategoryCreateRequest
from app.email_service.types.category import EmailCategoryList
from app.email_service.types.draft import EmailReplyDraftRequest
from app.email_service.types.message import EmailMessage
from app.email_service.types.thread import EmailThread
from app.email_service.types.thread import EmailThreadRequest


class GmailProvider(EmailProvider):

    def __init__(self, account: EmailAccount) -> None:
        self._gmail = GmailService(GmailTokenManager(account))

    def get_message(self, message_id: str) -> EmailMessage:
        return self._gmail.get_message(MessageRequest(id=message_id)).to_email()

    def get_thread(self, thread_request: EmailThreadRequest) -> EmailThread:
        return self._gmail.get_thread(ThreadRequest.from_email_draft_request(thread_request)).to_email_thread()

    def get_category(self, category_id: str) -> EmailCategory:
        return self._gmail.get_label(category_id).to_email_category()

    def get_categories(self) -> EmailCategoryList:
        return self._gmail.get_labels().to_email_categories()

    def create_category(self, category_request: EmailCategoryCreateRequest) -> EmailCategory:
        label_request = LabelCreateRequest.from_email_category_create_request(category_request)
        return self._gmail.post_label(label_request).to_email_category()

    def assign_category(self, message_id: str, category_id: str) -> None:
        self._gmail.modify_message(MessageModifyRequest(id=message_id, addLabelIds=[category_id]))

    def create_draft(self, draft_request: EmailReplyDraftRequest) -> str:
        return self._gmail.post_draft(DraftCreateRequest.from_email_draft_create_request(draft_request)).id
