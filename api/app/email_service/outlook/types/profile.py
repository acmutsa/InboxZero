
from typing import Optional
from pydantic import BaseModel


class Profile(BaseModel):
    emailAddress: str
    messagesTotal: int = 0
    displayName: Optional[str] = None
