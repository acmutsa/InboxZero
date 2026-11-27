from pydantic import BaseModel
from pydantic import ConfigDict


class EmailReplyDraftRequest(BaseModel):
    reply_to_id: str | None = None   
    thread_id: str         
    to: list[str]         
    cc: list[str] = []
    subject: str                     
    body: str
    is_html: bool = False
    references: list[str] = []        # Gmail: References chain