from typing import Optional
from pydantic import BaseModel

class MessageListRequest(BaseModel):
    labelIds: Optional[list[str]] = None
    q: Optional[str] = None
    pageToken: Optional[str] = None
    maxResults: int = 100
