from typing_extensions import TypedDict
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.ai_pipeline.thread_context import PreviousMessage
from app.ai_pipeline.thread_context import ThreadContext
from app.ai_pipeline.user_context import UserContext


class BinValidate(BaseModel):
    needs_reply: bool
    confidence: float = Field(ge=0.0, le=1.0)   # rejects anything outside 0–1
    reason: str

class DraftValidate(BaseModel):
    """The drafter's output, matching the JSON the drafting prompt asks for."""

    model_config = ConfigDict(str_strip_whitespace=True)

    subject: str = Field(min_length=1)
    body: str = Field(min_length=1)             # whitespace-only is rejected too
    # Bracketed gaps the user must fill in, e.g. "[time that works]".
    placeholders: list[str] = []
    # Sensitive message or a decision left to the user. Never sent automatically.
    needs_review: bool

    @model_validator(mode="after")
    def placeholders_appear_in_body(self) -> "DraftValidate":
        missing = [p for p in self.placeholders if p not in self.body]
        if missing:
            raise ValueError(f"placeholders not found in body: {missing}")
        return self


# Every key a node returns must be declared here: LangGraph silently drops
# updates to keys that are not in the state schema.
class EmailState(TypedDict):
    user: UserContext           # who the reply is for; fills the prompt placeholders
    label_ids: list[str]        # was str
    headers: dict               # header names lowercased
    body: str                   # quoted history removed, length-capped
    thread: ThreadContext       # from Gmail at processing time; not stored in the DB
    previous_message: PreviousMessage | None  # the message before this one in the thread
    raw_output: str | None      # was str
    parsed: dict | None
    bin_result: BinValidate | None      # set by the binning gate
    draft_result: DraftValidate | None  # set by the drafting gate
    skip_reason: str | None     # set by a gate that decides not to reply
    error: str | None
    attempts: int               # failed tries of the current LLM step; reset on success
