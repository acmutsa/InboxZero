from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class EmailAddress(BaseModel):
    address: Optional[str] = None
    name: Optional[str] = None

class Recipient(BaseModel):
    emailAddress: EmailAddress

class ItemBody(BaseModel):
    contentType: str  # "html" or "text"
    content: str

class MessageHeader(BaseModel):
    name: str
    value: str

class Message(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    conversationId: Optional[str] = None
    parentFolderId: Optional[str] = None
    subject: Optional[str] = None
    bodyPreview: Optional[str] = None
    body: Optional[ItemBody] = None
    from_user: Optional[Recipient] = Field(None, alias="from")
    replyTo: list[Recipient] = []
    toRecipients: list[Recipient] = []
    ccRecipients: list[Recipient] = []
    bccRecipients: list[Recipient] = []
    categories: list[str] = []
    isRead: Optional[bool] = None
    isDraft: Optional[bool] = None
    hasAttachments: Optional[bool] = None
    receivedDateTime: Optional[datetime] = None
    sentDateTime: Optional[datetime] = None

    @property
    def text(self) -> Optional[str]:
        return self.get_body("text/plain") or self.get_body("text/html")

    def get_body(self, mime_type: Literal["text/plain", "text/html"] = "text/plain") -> Optional[str]:
        if self.body is None: return None
        wanted = "text" if mime_type == "text/plain" else "html"
        return self.body.content if self.body.contentType.lower() == wanted else None
