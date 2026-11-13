import base64
import Iterator
import datetime
import timezone
import Literal
from typing import Optional
from pydantic import BaseModel

class MessageHeader(BaseModel):
    name: str
    value: str

class MessageBody(BaseModel):
    attachmentId: Optional[str] = None
    size: int = 0
    data: Optional[str] = None                     

class MessagePart(BaseModel):
    partId: Optional[str] = None
    mimeType: Optional[str] = None
    filename: Optional[str] = None
    headers: list[MessageHeader] = []
    body: Optional[MessageBody] = None
    parts: Optional[list["MessagePart"]] = None  

    def walk(self) -> Iterator["MessagePart"]:
        yield self
        for child in self.parts or []:
            yield from child.walk()

class Message(BaseModel):
    id: str
    threadId: Optional[str] = None
    labelIds: list[str] = []
    snippet: Optional[str] = None
    historyId: Optional[str] = None
    internalDate: Optional[str] = None      
    payload: Optional[MessagePart] = None         
                      
    @property
    def subject(self) -> Optional[str]:
        return self.header("Subject")

    @property
    def sender(self) -> Optional[str]:
        return self.header("From")
    
    @property
    def cc(self) -> Optional[str]:
        return self.header("Cc")
        
    @property
    def bcc(self) -> Optional[str]: 
        return self.header("Bcc")

    @property
    def text(self) -> Optional[str]:
        return self.body("text/plain") or self.body("text/html")

    @property
    def received_at(self) -> Optional[datetime]:
        if self.internalDate is None:
            return None
        return datetime.fromtimestamp(int(self.internalDate) / 1000, tz=timezone.utc)

    @property
    def is_unread(self) -> bool:
        return "UNREAD" in self.labelIds

    def header(self, name: str) -> Optional[str]:
        if self.payload is None: return None
        wanted = name.lower()
        return next((header.value for header in self.payload.headers if header.name.lower() == wanted), None)

    def body(self, mime_type: Literal["text/plain", "text/html"] = "text/plain") -> Optional[str]:
        if self.payload is None: return None
        for part in self.payload.walk():
            if part.mimeType == mime_type and not part.filename and part.body and part.body.data:
                return self.decode_base64url(part.body.data).decode("utf-8", errors="replace")
        return None

    def decode_base64url(self, data: str) -> bytes:
        return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))