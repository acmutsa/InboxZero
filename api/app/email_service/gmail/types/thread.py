from typing import Optional
from pydantic import BaseModel

from app.email_service.gmail.types.message import Message

class ThreadRequest(BaseModel):
    id: str  
    format: str = "full"          

class ThreadListRequest(BaseModel):
    labelIds: Optional[list[str]] = None
    q: Optional[str] = None
    pageToken: Optional[str] = None
    maxResults: int = 100


class Thread(BaseModel):
    id: str
    snippet: Optional[str] = None
    historyId: Optional[str] = None
    messages: list[Message] = []


class ThreadList(BaseModel):
    threads: list[Thread] = []
    nextPageToken: Optional[str] = None
    resultSizeEstimate: Optional[int] = None
