from pydantic import BaseModel

class AuthorizationUrl(BaseModel):
    authorization_url: str
