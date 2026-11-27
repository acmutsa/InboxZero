import uuid

from typing_extensions import TypedDict

from  app.ai_pipeline.types.bin_validate import BinValidate
from  app.ai_pipeline.types.draft_validate import DraftValidate

from app.email_service.types.message import EmailMessage
from app.email_service.types.thread import EmailThread
from app.models.user_context import CategoryOption
from app.models.user_context import UserContext
from app.email_service.provider import EmailProvider

class EmailState(TypedDict):
    user: UserContext           
    provider: EmailProvider | None
    email_id: uuid.UUID | None  
    message_id: str             
    label_ids: list[str]        
    headers: dict               
    body: str                   
    message: EmailMessage
    thread: EmailThread
    previous_message: EmailMessage | None
    raw_output: str | None      
    parsed: dict | None
    bin_result: BinValidate | None      
    draft_result: DraftValidate | None  
    skip_reason: str | None    
    categorize_skip_reason: str | None
    category: CategoryOption | None     
    error: str | None
    attempts: int               