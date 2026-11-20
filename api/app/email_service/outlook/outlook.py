
import requests
from urllib.parse import quote

from app.email_service.outlook.types.draft import (
    DraftRequest,
    DraftResponse,
    DraftListResponse,
)
from app.email_service.outlook.types.label import (
    LabelRequest,
    LabelResponse,
    LabelListResponse,
    LabelColor,
)
from app.email_service.outlook.types.message import (
    MessageRequest,
    MessageResponse,
    MessageModifyRequest,
    MessageListResponse,
)
from app.email_service.outlook.types.profile import Profile
from app.email_service.outlook.types.error import OutlookServiceError


BASE_URL = "https://graph.microsoft.com/v1.0"


class OutlookService:

    def __init__(self, access_token: str):
        self.access_token = access_token

    def _request(self, method, endpoint, **kwargs):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

        response = requests.request(
            method,
            BASE_URL + endpoint,
            headers=headers,
            timeout=30,
            **kwargs,
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            raise OutlookServiceError(
                str(error),
                response.status_code,
            ) from error

        if not response.content:
            return None

        return response.json()

    @staticmethod
    def _message_path(message_id: str):
        return "/me/messages/" + quote(message_id, safe="")

    # ------------------------------
    # PROFILE
    # ------------------------------

    def get_profile(self) -> Profile:
        user = self._request("GET", "/me")

        mailbox = self._request(
            "GET",
            "/me/mailFolders/inbox",
        )

        return Profile(
            emailAddress=(
                user.get("mail")
                or user.get("userPrincipalName")
            ),
            messagesTotal=mailbox.get("totalItemCount", 0),
            displayName=user.get("displayName"),
        )

    # ------------------------------
    # LABELS / CATEGORIES
    # ------------------------------

    def get_labels(self) -> LabelListResponse:
        data = self._request(
            "GET",
            "/me/outlook/masterCategories",
        )

        labels = [
            LabelResponse(
                id=item["id"],
                name=item["displayName"],
                color=LabelColor(
                    color=item.get("color", "preset0")
                ),
            )
            for item in data.get("value", [])
        ]

        return LabelListResponse(labels=labels)

    def get_label(self, label_id: str) -> LabelResponse:
        data = self._request(
            "GET",
            "/me/outlook/masterCategories/"
            + quote(label_id, safe=""),
        )

        return LabelResponse(
            id=data["id"],
            name=data["displayName"],
            color=LabelColor(
                color=data.get("color", "preset0")
            ),
        )

    def create_label(
        self,
        label: LabelRequest,
    ) -> LabelResponse:

        if not label.name:
            raise ValueError("Label name is required")

        payload = {
            "displayName": label.name,
            "color": (
                label.color.color
                if label.color
                else "preset0"
            ),
        }

        data = self._request(
            "POST",
            "/me/outlook/masterCategories",
            json=payload,
        )

        return LabelResponse(
            id=data["id"],
            name=data["displayName"],
            color=LabelColor(
                color=data.get("color", "preset0")
            ),
        )

    def delete_label(self, label_id: str) -> None:
        self._request(
            "DELETE",
            "/me/outlook/masterCategories/"
            + quote(label_id, safe=""),
        )

    # ------------------------------
    # MESSAGES
    # ------------------------------

    def get_messages(
        self,
        top: int = 20,
    ) -> MessageListResponse:

        data = self._request(
            "GET",
            "/me/messages",
            params={"$top": top},
        )

        messages = [
            MessageResponse.model_validate(item)
            for item in data.get("value", [])
        ]

        return MessageListResponse(
            messages=messages,
            resultSizeEstimate=len(messages),
            nextPageToken=data.get("@odata.nextLink"),
        )

    def get_message(
        self,
        message_id: str,
    ) -> MessageResponse:

        data = self._request(
            "GET",
            self._message_path(message_id),
        )

        return MessageResponse.model_validate(data)

    def modify_message(
        self,
        message_id: str,
        modification: MessageModifyRequest,
    ) -> MessageResponse:

        endpoint = self._message_path(message_id)

        message = self._request("GET", endpoint)

        categories = set(
            message.get("categories", [])
        )

        # Resolve master-category IDs to their names.
        category_data = self._request(
            "GET",
            "/me/outlook/masterCategories",
        )

        id_to_name = {
            item["id"]: item["displayName"]
            for item in category_data.get("value", [])
        }

        for label_id in modification.addLabelIds:
            categories.add(
                id_to_name.get(label_id, label_id)
            )

        for label_id in modification.removeLabelIds:
            categories.discard(
                id_to_name.get(label_id, label_id)
            )

        updated = self._request(
            "PATCH",
            endpoint,
            json={"categories": sorted(categories)},
        )

        return MessageResponse.model_validate(updated)

    # ------------------------------
    # DRAFTS
    # ------------------------------

    def get_drafts(self) -> DraftListResponse:
        data = self._request(
            "GET",
            "/me/mailFolders/drafts/messages",
        )

        drafts = [
            DraftResponse(
                id=item["id"],
                message=MessageResponse.model_validate(item),
            )
            for item in data.get("value", [])
        ]

        return DraftListResponse(
            drafts=drafts,
            nextPageToken=data.get("@odata.nextLink"),
            resultSizeEstimate=len(drafts),
        )

    def get_draft(
        self,
        draft_id: str,
    ) -> DraftResponse:

        message = self.get_message(draft_id)

        if message.isDraft is not True:
            raise OutlookServiceError(
                "This message is not a draft",
                400,
            )

        return DraftResponse(
            id=message.id,
            message=message,
        )

    def create_draft(
        self,
        draft: DraftRequest,
    ) -> DraftResponse:

        payload = draft.message.model_dump(
            exclude_none=True
        )

        data = self._request(
            "POST",
            "/me/messages",
            json=payload,
        )

        return DraftResponse(
            id=data["id"],
            message=MessageResponse.model_validate(data),
        )

    def send_draft(self, draft_id: str) -> None:
        self._request(
            "POST",
            self._message_path(draft_id) + "/send",
        )

    # ------------------------------
    # SEND EMAIL
    # ------------------------------

    def send_message(
        self,
        message: MessageRequest,
    ) -> None:

        self._request(
            "POST",
            "/me/sendMail",
            json={
                "message": message.model_dump(
                    exclude_none=True
                ),
                "saveToSentItems": True,
            },
        )
