import base64

from email.message import EmailMessage as MimeMessage
from typing import Optional
from pydantic import BaseModel

from app.email_service.gmail.types.message import Message
from app.email_service.types.draft import EmailReplyDraftRequest

class DraftMessage(BaseModel):
    raw: str
    threadId: Optional[str] = None

class DraftCreateRequest(BaseModel):
    message: DraftMessage

    @classmethod
    def from_email_draft_create_request(cls, request: EmailReplyDraftRequest) -> DraftCreateRequest:
        mime = MimeMessage()
        mime["To"] = ", ".join(request.to)
        if request.cc:
            mime["Cc"] = ", ".join(request.cc)
        mime["Subject"] = request.subject
        if request.in_reply_to:
            mime["In-Reply-To"] = request.in_reply_to
        if request.references:
            mime["References"] = " ".join(request.references)
        mime.set_content(request.body, subtype="html" if request.is_html else "plain")
        raw = base64.urlsafe_b64encode(mime.as_bytes()).decode("ascii")

        return cls(
            message=DraftMessage(raw=raw, threadId=request.thread_id)
        )


class DraftUpdateRequest(BaseModel):
    id: str
    message: DraftMessage

class DraftRequest(BaseModel):                    
    id: str
    format: str = "full"

class DraftListRequest(BaseModel):
    q: Optional[str] = None
    pageToken: Optional[str] = None
    maxResults: int = 100                     

class Draft(BaseModel):
    id: str                                       
    message: Optional[Message] = None   

class DraftList(BaseModel):
    drafts: list[Draft] = []              
    nextPageToken: Optional[str] = None
    resultSizeEstimate: Optional[int] = None