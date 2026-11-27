from app.db.schema import EmailAccount

from app.email_service.outlook.outlook import OutlookService
from app.email_service.outlook.token_manager import OutlookTokenManager
from app.email_service.outlook.types.draft import DraftCreateRequest
from app.email_service.outlook.types.mail_folder import MailFolderCreateRequest
from app.email_service.outlook.types.message_modify_request import MessageMoveRequest
from app.email_service.outlook.types.message_request import MessageRequest
from app.email_service.outlook.types.thread import ThreadRequest

from app.email_service.provider import EmailProvider
from app.email_service.types.category import EmailCategory
from app.email_service.types.category import EmailCategoryCreateRequest
from app.email_service.types.category import EmailCategoryList
from app.email_service.types.draft import EmailReplyDraftRequest
from app.email_service.types.message import EmailMessage
from app.email_service.types.thread import EmailThread
from app.email_service.types.thread import EmailThreadRequest


class OutlookProvider(EmailProvider):

    def __init__(self, account: EmailAccount) -> None:
        self._outlook = OutlookService(OutlookTokenManager(account))

    def get_message(self, message_id: str) -> EmailMessage:
        return self._outlook.get_message(MessageRequest(id=message_id)).to_email()

    def get_thread(self, thread_request: EmailThreadRequest) -> EmailThread:
        thread = self._outlook.get_thread(ThreadRequest.from_email_draft_request(thread_request))
        return thread.to_email_thread(thread_request.id)   # Graph has no thread object, so the id is passed in

    def get_category(self, category_id: str) -> EmailCategory:
        return self._outlook.get_mail_folder(category_id).to_email_category()

    def get_categories(self) -> EmailCategoryList:
        return self._outlook.get_mail_folders().to_email_categories()

    def create_category(self, category_request: EmailCategoryCreateRequest) -> EmailCategory:
        folder_request = MailFolderCreateRequest.from_email_category_create_request(category_request)
        return self._outlook.post_mail_folder(folder_request).to_email_category()

    def assign_category(self, message_id: str, category_id: str) -> None:
        self._outlook.move_message(MessageMoveRequest(id=message_id, destinationId=category_id))

    def create_draft(self, draft_request: EmailReplyDraftRequest) -> str:
        return self._outlook.create_draft(DraftCreateRequest.from_email_draft_create_request(draft_request)).id
