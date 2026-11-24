from pydantic import BaseModel

class OutlookCallbackRequest(BaseModel):
    code: str
    state: str
