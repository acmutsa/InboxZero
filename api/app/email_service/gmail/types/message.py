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

class MessageRequest(BaseModel):
    raw: str                                       
    threadId: Optional[str] = None                

class MessageModifyRequest(BaseModel):
    addLabelIds: list[str] = []
    removeLabelIds: list[str] = []

class MessageResponse(BaseModel):
    id: str
    threadId: Optional[str] = None
    labelIds: list[str] = []
    snippet: Optional[str] = None
    historyId: Optional[str] = None
    internalDate: Optional[str] = None      
    sizeEstimate: Optional[int] = None
    payload: Optional[MessagePart] = None         
    raw: Optional[str] = None                   

class MessageListResponse(BaseModel):
    messages: list[MessageResponse] = []          
    nextPageToken: Optional[str] = None
    resultSizeEstimate: Optional[int] = None

