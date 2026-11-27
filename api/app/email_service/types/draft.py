from pydantic import BaseModel
from pydantic import ConfigDict


class EmailReplyDraftRequest(BaseModel):
    original_message_id: str          # Outlook: createReply/{id}
    thread_id: str                    # Gmail: threadId
    to: list[str]                     # "Sam Lee <sam@x.com>"
    cc: list[str] = []
    subject: str                      # "Re: Hi"
    body: str
    is_html: bool = False
    in_reply_to: str | None = None    # Gmail: original's Message-ID
    references: list[str] = []        # Gmail: References chain