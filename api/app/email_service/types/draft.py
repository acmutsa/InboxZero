from pydantic import BaseModel
from pydantic import ConfigDict


class ReplyDraft(BaseModel):
    model_config = ConfigDict(frozen=True)

    to_address: str
    subject: str
    body: str
