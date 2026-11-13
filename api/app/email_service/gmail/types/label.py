from typing import Literal, Optional
from pydantic import AfterValidator, BaseModel

class LablelCreateRequest(BaseModel):
    name: str
    labelListVisibility: Optional[Literal["labelShow", "labelShowIfUnread", "labelHide"]] = None
    messageListVisibility: Optional[Literal["show", "hide"]] = None
    color: Optional["LabelColor"] = None
    
class LabelColor(BaseModel):
    textColor: str
    backgroundColor:str

class Label(BaseModel):
    id: str
    name: str
    type: Optional[Literal["system", "user"]] = None
    messageListVisibility: Optional[Literal["show", "hide"]] = None
    labelListVisibility: Optional[Literal["labelShow", "labelShowIfUnread", "labelHide"]] = None
    color: Optional[LabelColor] = None
    
class LabelList(BaseModel):
    labels: list[Label] = []