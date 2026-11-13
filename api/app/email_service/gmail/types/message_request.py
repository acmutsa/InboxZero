from pydantic import BaseModel

class MessageRequest(BaseModel):
    id: str
    format: str = "full"
