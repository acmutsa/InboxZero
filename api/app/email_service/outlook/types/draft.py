from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.email_service.outlook.types.message import ItemBody
from app.email_service.outlook.types.message import Message
from app.email_service.outlook.types.message_request import MessageRequest

class DraftEmailAddress(BaseModel):
    address: EmailStr
    name: Optional[str] = None

class DraftRecipient(BaseModel):
    emailAddress: DraftEmailAddress

class DraftCreateRequest(BaseModel):
    subject: str
    body: ItemBody
    toRecipients: list[DraftRecipient] = []
    ccRecipients: list[DraftRecipient] = []
    bccRecipients: list[DraftRecipient] = []

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
