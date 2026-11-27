from pydantic import BaseModel

from app.email_service.outlook.types.message_list import MessageList
from app.email_service.types.thread import EmailThread
from app.email_service.types.thread import EmailThreadRequest

class ThreadRequest(BaseModel):
    id: str
    top: int = 3

    @classmethod
    def from_email_draft_request(cls, thread_request: EmailThreadRequest) -> ThreadRequest:
        return cls(
            id=thread_request.id,
            top=thread_request.top
        )

class Thread(MessageList):
    def to_email_thread(self, thread_id: str) -> EmailThread:
        return EmailThread(
            id=thread_id, 
            messages=[message.to_email() for message in self.value]
        )
