from pydantic import BaseModel

class DecodedOutlookState(BaseModel):
    sub: str
    outlook: str
    purpose: str
    jti: str
    iat: int
    exp: int
