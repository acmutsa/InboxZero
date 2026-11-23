from pydantic import BaseModel

from app.email_service.outlook.types.message_list import MessageList

class ThreadRequest(BaseModel):
    id: str 
    top: int = 10

class Thread(MessageList):
    pass
