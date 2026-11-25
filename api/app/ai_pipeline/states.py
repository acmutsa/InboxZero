import uuid

from typing_extensions import TypedDict
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.ai_pipeline.thread_context import PreviousMessage
from app.ai_pipeline.thread_context import ThreadContext
from app.ai_pipeline.user_context import CategoryOption
from app.ai_pipeline.user_context import UserContext
from app.email_service.provider import EmailProvider


class BinValidate(BaseModel):
    category: str | None = None
    needs_reply: bool
    confidence: float = Field(ge=0.0, le=1.0)   # rejects anything outside 0–1
    reason: str

class DraftValidate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    subject: str = Field(min_length=1)
    body: str = Field(min_length=1)             
    placeholders: list[str] = []
    needs_review: bool

    @model_validator(mode="after")
    def placeholders_appear_in_body(self) -> "DraftValidate":
        missing = [p for p in self.placeholders if p not in self.body]
        if missing:
            raise ValueError(f"placeholders not found in body: {missing}")
        return self

class EmailState(TypedDict):
    user: UserContext           
    provider: EmailProvider | None
    email_id: uuid.UUID | None  
    message_id: str             
    label_ids: list[str]        
    headers: dict               
    body: str                   
    thread: ThreadContext       
    previous_message: PreviousMessage | None  
    raw_output: str | None      
    parsed: dict | None
    bin_result: BinValidate | None      
    draft_result: DraftValidate | None  
    skip_reason: str | None    
    categorize_skip_reason: str | None
    category: CategoryOption | None     
    error: str | None
    attempts: int               