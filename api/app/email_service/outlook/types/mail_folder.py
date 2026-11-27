from typing import Annotated
from typing import Optional

from pydantic import AfterValidator
from pydantic import AnyHttpUrl
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from app.email_service.types.category import EmailCategory
from app.email_service.types.category import EmailCategoryList
from app.email_service.types.category import EmailCategoryCreateRequest

LinkStr = Annotated[AnyHttpUrl, AfterValidator(str)]

class MailFolderCreateRequest(BaseModel):
    displayName: str
    isHidden: Optional[bool] = False

    @classmethod
    def from_email_category_create_request(cls, category_request: EmailCategoryCreateRequest) -> MailFolderCreateRequest:
        return cls(
            displayName=category_request.name,
        )

class MailFolder(BaseModel):
    id: str
    displayName: Optional[str] = None
    parentFolderId: Optional[str] = None
    childFolderCount: Optional[int] = None
    totalItemCount: int = 0
    unreadItemCount: int = 0
    isHidden: Optional[bool] = None

    def to_email_category(self) -> EmailCategory:
        return EmailCategory(
            id=self.id,
            name=self.displayName or "",
            parent_id=self.parentFolderId,
        )

class MailFolderList(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    value: list[MailFolder] = []
    nextLink: Optional[LinkStr] = Field(None, alias="@odata.nextLink")

    def to_email_categories(self) -> EmailCategoryList:
        return EmailCategoryList(
            categories=[folder.to_email_category() for folder in self.value]
        )
