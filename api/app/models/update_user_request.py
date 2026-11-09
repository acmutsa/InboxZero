from pydantic import BaseModel

class UpdateUserRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
