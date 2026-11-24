from typing import Annotated, Optional
from pydantic import AfterValidator, AnyHttpUrl, BaseModel, ConfigDict, Field

LinkStr = Annotated[AnyHttpUrl, AfterValidator(str)]

class MailFolderCreateRequest(BaseModel):
    displayName: str
    isHidden: Optional[bool] = None

class MailFolder(BaseModel):
    id: str
    displayName: Optional[str] = None
    parentFolderId: Optional[str] = None
    childFolderCount: Optional[int] = None
    totalItemCount: int = 0
    unreadItemCount: int = 0
    isHidden: Optional[bool] = None

class MailFolderList(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    value: list[MailFolder] = []
    nextLink: Optional[LinkStr] = Field(None, alias="@odata.nextLink")
