from pydantic import BaseModel

class GmailCallbackRequest(BaseModel):
    code: str
    state: str