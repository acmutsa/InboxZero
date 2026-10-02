from typing import Annotated, Literal, Optional
from pydantic import AfterValidator, BaseModel

ALLOWED_COLORS = [
    "#000000", "#434343", "#666666", "#999999", "#cccccc", "#6d9eeb", "#b694e8", "#ffd6a2", "#68dfa9", 
    "#efefef", "#f3f3f3", "#ffffff", "#fb4c2f", "#ffad47", "#fad165", "#16a766", "#43d692", "#4a86e8", "#a479e2",
    "#f691b3", "#f6c5be", "#ffe6c7", "#fef1d1", "#b9e4d0", "#c6f3de", "#c9daf8", "#e4d7f5", "#fcdee8", "#efa093",
    "#fce8b3", "#89d3b2", "#a0eac9", "#a4c2f4", "#d0bcf1", "#fbc8d9", "#e66550", "#ffbc6b", "#fcda83", "#44b984", 
    "#eaa041", "#f2c960", "#149e60", "#f7a7c0", "#cc3a21", "#b694e8", "#b694e8", "#b694e8", "#b694e8", "#b694e8",
    "#ac2b16", "#cf8933", "#d5ae49", "#0b804b", "#2a9c68", "#285bac", "#3dc789", "#3c78d8", "#f2c960", "#149e60",
    "#653e9b", "#b65775", "#822111", "#a46a21", "#aa8831", "#076239", "#1a764d", "#1c4587", "#8e63ce", "#e07798", 
    "#41236d", "#83334c", "#464646", "#e7e7e7", "#0d3472", "#b6cff5", "#0d3b44", "#98d7e4", "#3d188e", "#e3d7ff",
    "#711a36", "#fbd3e0", "#8a1c0a", "#f2b2a8", "#7a2e0b", "#ffc8af", "#7a4706", "#ffdeb5", "#594c05", "#fbe983", 
    "#684e07", "#fdedc1", "#0b4f30", "#b3efd3", "#04502e", "#a2dcc1", "#c2c2c2", "#4986e7", "#2da2bb", "#b99aff", 
    "#994a64", "#f691b2", "#ff7537", "#ffad46", "#662e37", "#ebdbde", "#cca6ac", "#094228", "#42d692", "#16a765",
]
def check_color(v: str) -> str:
    v = v.lower()
    if v not in ALLOWED_COLORS:
        raise ValueError(f"{v} is not an allowed Gmail label color")
    return v

class LabelColor(BaseModel):
    textColor: Annotated[str, AfterValidator(check_color)]
    backgroundColor: Annotated[str, AfterValidator(check_color)]

class LabelRequest(BaseModel):                    
    name: Optional[str] = None                     
    messageListVisibility: Optional[Literal["show", "hide"]] = None
    labelListVisibility: Optional[Literal["labelShow", "labelShowIfUnread", "labelHide"]] = None
    color: Optional[LabelColor] = None

class LabelResponse(BaseModel):                    
    id: str
    name: str
    type: Optional[Literal["system", "user"]] = None
    messageListVisibility: Optional[Literal["show", "hide"]] = None
    labelListVisibility: Optional[Literal["labelShow", "labelShowIfUnread", "labelHide"]] = None
    messagesTotal: Optional[int] = None
    messagesUnread: Optional[int] = None
    threadsTotal: Optional[int] = None
    threadsUnread: Optional[int] = None
    color: Optional[LabelColor] = None

class LabelListResponse(BaseModel):
    labels: list[LabelResponse] = []