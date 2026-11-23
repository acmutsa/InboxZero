from pydantic import BaseModel

from app.email_service.outlook.types.message_list import MessageList

class ThreadRequest(BaseModel):
    id: str 

class Thread(MessageList):
    pass
