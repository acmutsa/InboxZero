from pydantic import BaseModel, EmailStr

class ConnectOutlookRequest(BaseModel):
    outlook: EmailStr
