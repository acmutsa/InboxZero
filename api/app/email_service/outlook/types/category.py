from typing import Optional
from pydantic import BaseModel

class CategoryCreateRequest(BaseModel):
    displayName: str
    color: Optional[str] = None   # "none" or "preset0" ... "preset24"

class Category(BaseModel):
    id: str
    displayName: str
    color: Optional[str] = None

class CategoryList(BaseModel):
    value: list[Category] = []
