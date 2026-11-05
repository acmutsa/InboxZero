from typing import Optional
from pydantic import BaseModel

from types.message import MessageResponse

class ThreadResponse(BaseModel):
    id: str
    snippet: Optional[str] = None
    historyId: Optional[str] = None
    messages: list[MessageResponse] = []
