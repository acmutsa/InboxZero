from pydantic import BaseModel

class DecodedGoogleState(BaseModel):
    sub: str
    gmail: str
    purpose: str
    jti: str
    iat: int
    exp: int
