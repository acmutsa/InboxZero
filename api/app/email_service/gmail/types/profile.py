from pydantic import BaseModel

class Profile(BaseModel):
    emailAddress: str
    messagesTotal: int
