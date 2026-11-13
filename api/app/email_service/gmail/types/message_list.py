from typing import Optional
from pydantic import BaseModel
from app.email_service.gmail.types.message import Message

class MessageList(BaseModel):
    messages: list[Message] = []
    nextPageToken: Optional[str] = None
