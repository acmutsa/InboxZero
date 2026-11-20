
from typing import Optional
from pydantic import BaseModel, Field


class LabelColor(BaseModel):
    color: str = "preset0"


class LabelRequest(BaseModel):
    name: Optional[str] = None
    color: Optional[LabelColor] = None


class LabelResponse(BaseModel):
    id: str
    name: str
    color: Optional[LabelColor] = None


class LabelListResponse(BaseModel):
    labels: list[LabelResponse] = Field(default_factory=list)
