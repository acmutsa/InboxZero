from typing import Optional
from pydantic import BaseModel

class MessageUpdateRequest(BaseModel):
    id: str
    categories: Optional[list[str]] = None
    isRead: Optional[bool] = None
