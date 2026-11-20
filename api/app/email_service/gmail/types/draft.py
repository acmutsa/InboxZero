from typing import Optional
from pydantic import BaseModel

from app.email_service.gmail.types.message import Message

class DraftMessage(BaseModel):
    raw: str
    threadId: Optional[str] = None

class DraftCreateRequest(BaseModel):
    message: DraftMessage

class DraftUpdateRequest(BaseModel):
    id: str
    message: DraftMessage

class DraftRequest(BaseModel):                    
    id: str
    format: str = "full"

class DraftListRequest(BaseModel):
    q: Optional[str] = None
    pageToken: Optional[str] = None
    maxResults: int = 100                     

class Draft(BaseModel):
    id: str                                       
    message: Optional[Message] = None   

class DraftList(BaseModel):
    drafts: list[Draft] = []              
    nextPageToken: Optional[str] = None
    resultSizeEstimate: Optional[int] = None