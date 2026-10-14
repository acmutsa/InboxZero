from pydantic import BaseModel

class ConnectGmailRequest(BaseModel):
    gmail: str