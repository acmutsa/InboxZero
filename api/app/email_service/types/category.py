from pydantic import BaseModel

class EmailCategory(BaseModel):
    id: str
    name: str
    parent_id: str | None = None   
    is_system: bool = False        

class EmailCategoryList(BaseModel):
    categories: list[EmailCategory] = []

class EmailCategoryCreateRequest(BaseModel):
    name: str
    color: str | None = None
