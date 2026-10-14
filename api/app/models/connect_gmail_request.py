from pydantic import BaseModel

class ConnectGmailRequest(BaseModel):
    login_hint: str 