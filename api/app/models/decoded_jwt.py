from pydantic import BaseModel

class DecodedJWT(BaseModel):
    user_id: str
    gmail: str
    purpose: str 