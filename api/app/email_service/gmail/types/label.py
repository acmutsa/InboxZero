from typing import Literal
from typing import Optional
from pydantic import BaseModel
from app.email_service.types.category import EmailCategory
from app.email_service.types.category import EmailCategoryList
from app.email_service.types.category import EmailCategoryCreateRequest

class LabelCreateRequest(BaseModel):
    name: str
    labelListVisibility: Optional[Literal["labelShow", "labelShowIfUnread", "labelHide"]] = None
    messageListVisibility: Optional[Literal["show", "hide"]] = None
    color: Optional["LabelColor"] = None

    @classmethod
    def from_email_category_create_request(cls, category: EmailCategoryCreateRequest) -> LabelCreateRequest:
        return cls(
            name=category.name,
        )
    
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

    def to_email_category(self) -> EmailCategory:
        return EmailCategory(
            id=self.id,
            name=self.name,
            is_system=self.type == "system",
        )

class LabelList(BaseModel):
    labels: list[Label] = []

    def to_email_categories(self) -> EmailCategoryList:
        return EmailCategoryList(
            categories=[label.to_email_category() for label in self.labels]
        )
