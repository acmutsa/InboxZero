import base64

from email.message import EmailMessage as MimeMessage
from email.utils import formataddr
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.email_service.outlook.types.message import ItemBody
from app.email_service.outlook.types.message import Message
from app.email_service.outlook.types.message_request import MessageRequest
from app.email_service.types.draft import EmailReplyDraftRequest

class DraftEmailAddress(BaseModel):
    address: EmailStr
    name: Optional[str] = None

class DraftRecipient(BaseModel):
    emailAddress: DraftEmailAddress

class DraftCreateRequest(BaseModel):
    id: str     # the message being replied to
    mime: str

    @classmethod
    def from_email_draft_create_request(cls, request: EmailReplyDraftRequest) -> DraftCreateRequest:
        mime = MimeMessage()
        mime["To"] = ", ".join(request.to)
        if request.cc:
            mime["Cc"] = ", ".join(request.cc)
        mime["Subject"] = request.subject
        if request.in_reply_to:
            mime["In-Reply-To"] = request.in_reply_to
        if request.references:
            mime["References"] = " ".join(request.references)
        mime.set_content(request.body, subtype="html" if request.is_html else "plain")

        return DraftCreateRequest(
            id=request.original_message_id, mime=base64.b64encode(mime.as_bytes()).decode("ascii")
        )

class DraftRequest(MessageRequest):
    pass

class DraftListRequest(BaseModel):
    top: int = 10
    
class Draft(Message):
    pass

class DraftList(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    value: list[Draft] = []
    nextLink: Optional[str] = Field(None, alias="@odata.nextLink")
    count: Optional[int] = Field(None, alias="@odata.count")
