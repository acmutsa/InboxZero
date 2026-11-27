
from pydantic import BaseModel, Field


class BinValidate(BaseModel):
    category: str | None = None
    needs_reply: bool
    confidence: float = Field(ge=0.0, le=1.0)   # rejects anything outside 0–1
    reason: str

