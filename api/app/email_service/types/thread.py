from pydantic import BaseModel
from pydantic import ConfigDict

from app.email_service.types.message import EmailMessage

class EmailThreadRequest(BaseModel):
    id: str
    top: int = 3

class EmailThread(BaseModel):
    id: str
    messages: list[EmailMessage] = []
