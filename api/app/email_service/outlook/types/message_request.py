from pydantic import BaseModel

class MessageRequest(BaseModel):
    id: str
