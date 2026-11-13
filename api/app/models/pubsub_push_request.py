from typing import Optional
from pydantic import BaseModel

class PubSubMessage(BaseModel):
    data: Optional[str] = None
    messageId: Optional[str] = None
    publishTime: Optional[str] = None
    attributes: dict[str, str] = {}

class PubSubPushRequest(BaseModel):
    message: PubSubMessage
    subscription: Optional[str] = None
