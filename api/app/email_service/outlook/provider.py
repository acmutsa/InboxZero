from email.utils import getaddresses

from app.db.schema import EmailAccount
from app.email_service.outlook.convert import OutlookFolderIds
from app.email_service.outlook.convert import to_email_message
from app.email_service.outlook.convert import to_email_thread
from app.email_service.outlook.outlook import MAX_PAGE_SIZE
from app.email_service.outlook.outlook import OutlookService
from app.email_service.outlook.token_manager import OutlookTokenManager
from app.email_service.outlook.types.category import CategoryCreateRequest
from app.email_service.outlook.types.draft import ReplyCreateRequest
from app.email_service.outlook.types.draft import ReplyMessage
from app.email_service.outlook.types.error import OutlookServiceError
from app.email_service.outlook.types.message import EmailAddress
from app.email_service.outlook.types.message import ItemBody
from app.email_service.outlook.types.message import Recipient
from app.email_service.outlook.types.message_modify_request import MessageUpdateRequest
from app.email_service.outlook.types.message_request import MessageRequest
from app.email_service.outlook.types.thread import ThreadRequest
from app.email_service.provider import EmailProvider
from app.email_service.types.draft import ReplyDraft
from app.email_service.types.message import EmailMessage
from app.email_service.types.thread import EmailThread


class OutlookProvider(EmailProvider):
    def __init__(self, account: EmailAccount) -> None:
        self._outlook = OutlookService(OutlookTokenManager(account))
        self._folders: OutlookFolderIds | None = None

    def get_message(self, message_id: str) -> EmailMessage:
        return to_email_message(self._outlook.get_message(MessageRequest(id=message_id)), self._folder_ids())

    def get_thread(self, thread_id: str) -> EmailThread:
        page = self._outlook.get_thread(ThreadRequest(id=thread_id, top=MAX_PAGE_SIZE))
        return to_email_thread(thread_id, page.value, self._folder_ids())

    def create_reply_draft(self, original: EmailMessage, reply: ReplyDraft) -> str:
        draft = self._outlook.create_reply(ReplyCreateRequest(
            id=original.id,
            message=ReplyMessage(
                subject=reply.subject,
                body=ItemBody(contentType="text", content=reply.body),
                toRecipients=_recipients(reply.to_address),
            ),
        ))
        return draft.id

    def apply_category(self, message_id: str, category_name: str) -> None:
        self._ensure_master_category(category_name)
        current = self._outlook.get_message(MessageRequest(id=message_id)).categories
        if any(name.lower() == category_name.lower() for name in current):
            return
        self._outlook.update_message(MessageUpdateRequest(id=message_id, categories=[*current, category_name]))

    def _ensure_master_category(self, category_name: str) -> None:
        wanted = category_name.lower()
        if any(category.displayName.lower() == wanted for category in self._outlook.get_categories().value):
            return
        try:
            self._outlook.post_category(CategoryCreateRequest(displayName=category_name))
        except OutlookServiceError as error:
            if error.status_code != 409:
                raise

    def _folder_ids(self) -> OutlookFolderIds:
        if self._folders is None:
            self._folders = OutlookFolderIds(
                sent=self._outlook.get_mail_folder("sentitems").id,
                junk=self._outlook.get_mail_folder("junkemail").id,
                deleted=self._outlook.get_mail_folder("deleteditems").id,
            )
        return self._folders


def _recipients(addresses: str) -> list[Recipient]:
    return [
        Recipient(emailAddress=EmailAddress(address=address, name=name or None))
        for name, address in getaddresses([addresses])
        if address
    ]
