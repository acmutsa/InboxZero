from typing import Optional
from pydantic import BaseModel

from app.email_service.gmail.types.message import Message
from app.email_service.types.thread import EmailThread
from app.email_service.types.thread import EmailThreadRequest

class ThreadRequest(BaseModel):
    id: str  
    format: str = "full"  

    @classmethod
    def from_email_draft_request(cls, thread_request: EmailThreadRequest) -> ThreadRequest:
        return cls(
            id=thread_request.id
        )

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

    def to_email_thread(self) -> EmailThread:
        return EmailThread(
            id=self.id, 
            messages=[message.to_email() for message in self.messages]
        )


class ThreadList(BaseModel):
    threads: list[Thread] = []
    nextPageToken: Optional[str] = None
    resultSizeEstimate: Optional[int] = None
