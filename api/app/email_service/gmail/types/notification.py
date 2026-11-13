from pydantic import BaseModel

class GmailNotification(BaseModel):
    emailAddress: str
    historyId: int
