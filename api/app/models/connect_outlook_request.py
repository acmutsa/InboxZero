from pydantic import BaseModel

class ConnectOutlookRequest(BaseModel):
    outlook: str
