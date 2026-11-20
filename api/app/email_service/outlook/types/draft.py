
from typing import Optional
from pydantic import BaseModel, Field

from .message import MessageRequest, MessageResponse


class DraftRequest(BaseModel):
    message: MessageRequest


class DraftResponse(BaseModel):
    id: str
    message: Optional[MessageResponse] = None


class DraftListResponse(BaseModel):
    drafts: list[DraftResponse] = Field(default_factory=list)
    nextPageToken: Optional[str] = None
    resultSizeEstimate: Optional[int] = None
