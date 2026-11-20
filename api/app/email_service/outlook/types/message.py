
from typing import Optional
from pydantic import BaseModel, Field


class MessageHeader(BaseModel):
    name: str
    value: str


class MessageBody(BaseModel):
    contentType: str = "HTML"
    content: str = ""


class EmailAddress(BaseModel):
    address: str
    name: Optional[str] = None


class Recipient(BaseModel):
    emailAddress: EmailAddress


class MessageRequest(BaseModel):
    subject: str
    body: MessageBody
    toRecipients: list[Recipient] = Field(
        default_factory=list
    )
    ccRecipients: list[Recipient] = Field(
        default_factory=list
    )
    bccRecipients: list[Recipient] = Field(
        default_factory=list
    )


class MessageModifyRequest(BaseModel):
    addLabelIds: list[str] = Field(
        default_factory=list
    )
    removeLabelIds: list[str] = Field(
        default_factory=list
    )


class MessageResponse(BaseModel):
    id: str
    subject: Optional[str] = None
    bodyPreview: Optional[str] = None
    body: Optional[MessageBody] = None
    fromAddress: Optional[Recipient] = Field(
        default=None,
        alias="from"
    )
    toRecipients: list[Recipient] = Field(
        default_factory=list
    )
    categories: list[str] = Field(
        default_factory=list
    )
    isRead: Optional[bool] = None
    isDraft: Optional[bool] = None
    receivedDateTime: Optional[str] = None
    conversationId: Optional[str] = None


class MessageListResponse(BaseModel):
    messages: list[MessageResponse] = Field(
        default_factory=list
    )
    nextPageToken: Optional[str] = None
    resultSizeEstimate: Optional[int] = None
