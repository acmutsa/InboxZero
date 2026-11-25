import requests

from typing import Any
from urllib.parse import quote

from app.config import config
from app.email_service.outlook.token_manager import OutlookTokenManager

from app.email_service.outlook.types.error import OutlookServiceError
from app.email_service.outlook.types.user import User

from app.email_service.outlook.types.mail_folder import MailFolderList
from app.email_service.outlook.types.mail_folder import MailFolder
from app.email_service.outlook.types.mail_folder import MailFolderCreateRequest

from app.email_service.outlook.types.category import CategoryList
from app.email_service.outlook.types.category import Category
from app.email_service.outlook.types.category import CategoryCreateRequest

from app.email_service.outlook.types.message_list import MessageList
from app.email_service.outlook.types.message_list import MessageListRequest
from app.email_service.outlook.types.message import Message
from app.email_service.outlook.types.message_request import MessageRequest
from app.email_service.outlook.types.message_modify_request import MessageUpdateRequest

from app.email_service.outlook.types.draft import DraftList
from app.email_service.outlook.types.draft import Draft
from app.email_service.outlook.types.draft import DraftCreateRequest
from app.email_service.outlook.types.draft import DraftListRequest
from app.email_service.outlook.types.draft import DraftRequest

from app.email_service.outlook.types.thread import Thread
from app.email_service.outlook.types.thread import ThreadRequest

from app.email_service.outlook.types.subscription import Subscription
from app.email_service.outlook.types.subscription import SubscriptionCreateRequest
from app.email_service.outlook.types.subscription import SubscriptionRenewRequest

BASE_URL = "https://graph.microsoft.com/v1.0"
MAX_PAGE_SIZE = 50

PREFER_IMMUTABLE_ID = 'IdType="ImmutableId"'
PREFER_TEXT_BODY = 'outlook.body-content-type="text"'

class OutlookService:

    def __init__(self, token_manager: OutlookTokenManager) -> None:
        self.timeout = config.OUTLOOK_TIMEOUT_SECONDS
        self._session = token_manager.get_session()

    # HTTP
    def _get(self, path: str, params: dict[str, Any] | None = None, prefer: tuple[str, ...] = ()) -> dict[str, Any]:
        return self._request("GET", path, params=params, prefer=prefer)

    def _post(self, path: str, body: dict[str, Any] | None = None, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._request("POST", path, params=params, body=body)

    def _patch(self, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._request("PATCH", path, body=body)

    def _delete(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._request("DELETE", path, params=params)

    def _request(self, method: str, path: str, params: dict[str, Any] | None = None, body: dict[str, Any] | None = None, prefer: tuple[str, ...] = ()) -> dict[str, Any]:
        headers = {"Accept": "application/json", "Prefer": ", ".join((PREFER_IMMUTABLE_ID, *prefer))}

        try:
            response = self._session.request(method, BASE_URL + path, headers=headers, params=params, json=body, timeout=self.timeout)

        except requests.Timeout as error:
            raise OutlookServiceError("Outlook request timed out.", status_code=504) from error

        except requests.exceptions.SSLError as error:
            raise OutlookServiceError("Secure connection to Outlook failed.", status_code=502) from error

        except requests.ConnectionError as error:
            raise OutlookServiceError("Could not connect to Outlook.", status_code=503) from error

        except requests.exceptions.ChunkedEncodingError as error:
            raise OutlookServiceError("Connection to Outlook dropped while reading the response.", status_code=502) from error

        except requests.RequestException as error:
            raise OutlookServiceError("Outlook request failed.", status_code=502) from error

        if response.status_code == 401:
            raise OutlookServiceError("Outlook access was revoked or expired. Please connect Outlook again.", status_code=401)

        if not response.ok:
            raise OutlookServiceError("Outlook request failed.", status_code=response.status_code)

        if not response.content: return {}

        try:
            return response.json()

        except requests.JSONDecodeError as error:
            raise OutlookServiceError("Outlook returned an invalid response.", status_code=502) from error


    @staticmethod
    def _id(value: str) -> str:
        return quote(value, safe="")

    def get_verified_email(self) -> str:
        email = self.get_profile().email
        if not email:
            raise ValueError("Microsoft did not return an email address")

        return email


    # Profile
    def get_profile(self) -> User:
        return User.model_validate(self._get("/me"))


    # Mail folders
    def get_mail_folders(self, parent_folder_id: str | None = None, top: int = 100) -> MailFolderList:
        path = f"/me/mailFolders/{self._id(parent_folder_id)}/childFolders" if parent_folder_id else "/me/mailFolders"
        return MailFolderList.model_validate(self._get(path, {"$top": min(MAX_PAGE_SIZE, top)}))

    def get_mail_folder(self, folder_id: str = "inbox") -> MailFolder:
        return MailFolder.model_validate(self._get(f"/me/mailFolders/{self._id(folder_id)}"))

    def post_mail_folder(self, mailFolderCreateRequest: MailFolderCreateRequest) -> MailFolder:
        return MailFolder.model_validate(self._post("/me/mailFolders", body=mailFolderCreateRequest.model_dump(exclude_none=True)))

    def delete_mail_folder(self, folder_id: str) -> None:
        self._delete(f"/me/mailFolders/{self._id(folder_id)}")


    # Categories
    def get_categories(self) -> CategoryList:
        return CategoryList.model_validate(self._get("/me/outlook/masterCategories"))

    def get_category(self, category_id: str) -> Category:
        return Category.model_validate(self._get(f"/me/outlook/masterCategories/{self._id(category_id)}"))

    def post_category(self, categoryCreateRequest: CategoryCreateRequest) -> Category:
        return Category.model_validate(self._post("/me/outlook/masterCategories", body=categoryCreateRequest.model_dump(exclude_none=True)))

    def delete_category(self, category_id: str) -> None:
        self._delete(f"/me/outlook/masterCategories/{self._id(category_id)}")


    # Messages
    def get_messages(self, MessageListRequest: MessageListRequest) -> MessageList:
        return MessageList.model_validate(self._get("/me/messages", {"$top": min(MAX_PAGE_SIZE, MessageListRequest.top)}))

    def get_message(self, MessageRequest: MessageRequest) -> Message:
        return Message.model_validate(self._get(f"/me/messages/{self._id(MessageRequest.id)}",prefer=(PREFER_TEXT_BODY,)))

    def update_message(self, messageUpdateRequest: MessageUpdateRequest) -> Message:
        return Message.model_validate(self._patch(f"/me/messages/{self._id(messageUpdateRequest.id)}", body=messageUpdateRequest.model_dump(exclude={"id"}, exclude_none=True)))


    # Threads (Graph has no thread object for mailboxes. A thread is all messages with the same conversationId)
    def get_thread(self, threadRequest: ThreadRequest) -> Thread:
        return Thread.model_validate(self._get("/me/messages", {"$filter": f"conversationId eq '{threadRequest.id}'", "$top": threadRequest.top}))


    # Drafts (in Graph a draft is a Message with isDraft=true)
    def get_drafts(self, DraftListRequest: DraftListRequest) -> DraftList:
        return DraftList.model_validate(self._get("/me/mailFolders/drafts/messages", {"$top": min(MAX_PAGE_SIZE, DraftListRequest.top)}))

    def get_draft(self, DraftRequest: DraftRequest) -> Draft:
        draft = Draft.model_validate(self._get(f"/me/mailFolders/drafts/messages/{self._id(DraftRequest.id)}"))

        if draft.isDraft is not True:
            raise OutlookServiceError("This message is not a draft", status_code=400)

        return draft

    def create_draft(self, draftCreateRequest: DraftCreateRequest) -> Draft:
        return Draft.model_validate(self._post("/me/messages", body=draftCreateRequest.model_dump(exclude_none=True)))

    def send_draft(self, draft_id: str) -> None:
        self._post(f"/me/messages/{self._id(draft_id)}/send")

    def post_subscription(self, subscriptionCreateRequest: SubscriptionCreateRequest) -> Subscription:
        return Subscription.model_validate(self._post("/subscriptions", body=subscriptionCreateRequest.model_dump(mode="json")))

    def renew_subscription(self, subscriptionRenewRequest: SubscriptionRenewRequest) -> Subscription:
        return Subscription.model_validate(self._patch(f"/subscriptions/{self._id(subscriptionRenewRequest.id)}", body=subscriptionRenewRequest.model_dump(mode="json", exclude={"id"})))

    def delete_subscription(self, subscription_id: str) -> None:
        self._delete(f"/subscriptions/{self._id(subscription_id)}")
