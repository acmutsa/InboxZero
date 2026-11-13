import base64
import requests

from typing import Any
from typing import Literal

from google.auth.exceptions import GoogleAuthError
from google.auth.exceptions import RefreshError
from google.auth.exceptions import TransportError

from google.auth.transport.requests import AuthorizedSession

from collections.abc import Iterator

from app.config import config
from app.email_service.gmail.token_manager import GmailTokenManager

from app.email_service.gmail.types.profile import Profile
from app.email_service.gmail.types.error import GmailServiceError

from app.email_service.gmail.types.label import LabelList
from app.email_service.gmail.types.label import Label
from app.email_service.gmail.types.label import LablelCreateRequest

from app.email_service.gmail.types.message_list import MessageListRequest
from app.email_service.gmail.types.message_list import MessageList
from app.email_service.gmail.types.message import MessageRequest
from app.email_service.gmail.types.message import MessageModifyRequest
from app.email_service.gmail.types.message import MessageBody
from app.email_service.gmail.types.message import MessagePart
from app.email_service.gmail.types.message import Message

from app.email_service.gmail.types.draft import DraftList
from app.email_service.gmail.types.draft import Draft
from app.email_service.gmail.types.draft import DraftListRequest
from app.email_service.gmail.types.draft import DraftRequest
from app.email_service.gmail.types.draft import DraftCreateRequest

from app.email_service.gmail.types.thread import ThreadList
from app.email_service.gmail.types.thread import Thread
from app.email_service.gmail.types.thread import ThreadListRequest
from app.email_service.gmail.types.thread import ThreadRequest

BASE_URL = "https://gmail.googleapis.com/gmail/v1/users/me"
MAX_PAGE_SIZE = 500

class GmailService:

    def __init__(self, token_manager: GmailTokenManager) -> None:
        self.timeout = config.GMAIL_TIMEOUT_SECONDS
        self._session = token_manager.get_session()

    # HTTP
    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._request("GET", path, params=params)

    def _post(self, path: str, body: dict[str, Any] | None = None, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._request("POST", path, params=params, body=body)

    def _delete(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._request("DELETE", path, params=params)

    def _request(self, method: str, path: str, params: dict[str, Any] | None = None, body: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            response = self._session.request(method, BASE_URL + path, params=params, json=body, timeout=self.timeout)

        except RefreshError as error:
            raise GmailServiceError("Gmail access was revoked or expired. Please connect Gmail again.", status_code=401) from error

        except TransportError as error:
            raise GmailServiceError("Could not reach Google to refresh Gmail access.", status_code=503) from error

        except GoogleAuthError as error:
            raise GmailServiceError("Google authentication failed.", status_code=502) from error

        except requests.Timeout as error:
            raise GmailServiceError("Gmail request timed out.", status_code=504) from error

        except requests.exceptions.SSLError as error:
            raise GmailServiceError("Secure connection to Gmail failed.", status_code=502) from error

        except requests.ConnectionError as error:
            raise GmailServiceError("Could not connect to Gmail.", status_code=503) from error

        except requests.exceptions.ChunkedEncodingError as error:
            raise GmailServiceError("Connection to Gmail dropped while reading the response.", status_code=502) from error

        except requests.RequestException as error:
            raise GmailServiceError("Gmail request failed.", status_code=502) from error

        if not response.ok:
            raise GmailServiceError("Gmail request failed.", status_code=response.status_code)

        if not response.content: return {}

        try:
            return response.json()

        except requests.JSONDecodeError as error:
            raise GmailServiceError("Gmail returned an invalid response.", status_code=502) from error


    # Profile
    def get_profile(self) -> Profile:
        return Profile.model_validate(self._get("/profile"))


    # Labels
    def get_labels(self) -> list[Label]:
        return LabelList.model_validate(self._get("/labels")).labels

    def get_label(self, label_id: str) -> Label:
        return Label.model_validate(self._get(f"/labels/{label_id}"))
    
    def post_label(self, labelCreateRequest: LablelCreateRequest) -> Label:
        return Label.model_validate(self._post("/labels", body=labelCreateRequest.model_dump(exclude_unset=True)))
    
    def delete_label(self, label_id: str) -> None:
        self._delete(f"/labels/{label_id}")


    # Messages
    def get_messages(self, messageListRequest:MessageListRequest) -> MessageList:
        params = {
            "q": messageListRequest.q,
            "labelIds": messageListRequest.labelIds,
            "maxResults": min(MAX_PAGE_SIZE, messageListRequest.maxResults),
            "pageToken": messageListRequest.pageToken,
        }
        return MessageList.model_validate(self._get("/messages", params))

    def get_message(self, messageRequest:MessageRequest) -> Message:
        params = {
            "format": messageRequest.format,
        }
        return Message.model_validate(self._get(f"/messages/{messageRequest.id}", params))

    def modify_message(self, messageModifyRequest:MessageModifyRequest) -> Message:
        return Message.model_validate(self._post(f"/messages/{messageModifyRequest.id}/modify", body=messageModifyRequest.model_dump(exclude={"id"}, exclude_unset=True)))

    def get_attachment(self, message_id: str, attachment_id: str) -> bytes:
        body = MessageBody.model_validate(self._get(f"/messages/{message_id}/attachments/{attachment_id}"))
        return body.data 

    # Threads
    def get_threads(self, threadListRequest:ThreadListRequest) -> ThreadListResponse:
        params = {
            "q": threadListRequest.q,
            "labelIds": threadListRequest.labelIds,
            "maxResults": min(MAX_PAGE_SIZE, threadListRequest.maxResults),
            "pageToken": threadListRequest.pageToken,
        }
        return ThreadListResponse.model_validate(self._get("/threads", params))

    def get_thread(self, threadRequest:ThreadRequest) -> Thread:
        params = {
            "format": threadRequest.format,
        }
        return Thread.model_validate(self._get(f"/threads/{threadRequest.id}", params))

    # Drafts
    def get_drafts(self, draftListRequest:DraftListRequest) -> DraftListResponse:
        params = {
            "q": draftListRequest.q,
            "maxResults": min(MAX_PAGE_SIZE, draftListRequest.maxResults),
            "pageToken": draftListRequest.pageToken,
        }
        return DraftListResponse.model_validate(self._get("/drafts", params))

    def get_draft(self, draftRequest:DraftRequest) -> DraftResponse:
        return DraftResponse.model_validate(self._get(f"/drafts/{draftRequest.id}", {"format": draftRequest.format}))

    def post_draft(self, draftCreateRequest:DraftCreateRequest) -> DraftResponse:
        return DraftResponse.model_validate(self._post("/drafts", body=draftCreateRequest.model_dump(exclude_unset=True)))

    def delete_draft(self, draft_id: str) -> None:
        self._delete(f"/drafts/{draft_id}")

