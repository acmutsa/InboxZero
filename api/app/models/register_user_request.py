from pydantic import BaseModel

class RegisterUserRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
