from typing import Optional
from pydantic import BaseModel

class Profile(BaseModel):
    emailAddress: str
    messagesTotal: int
    threadsTotal: Optional[int] = None
    historyId: Optional[str] = None
