from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.email_service.outlook.types.message import Message

class MessageList(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    value: list[Message] = []
    nextLink: Optional[str] = Field(None, alias="@odata.nextLink")
    count: Optional[int] = Field(None, alias="@odata.count")
