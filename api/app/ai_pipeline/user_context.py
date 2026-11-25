import uuid

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import field_validator

FALLBACK_NAME = "user"


class CategoryOption(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: uuid.UUID | None = None
    name: str
    description: str | None = None


class UserContext(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    user_id: uuid.UUID | None = None
    email: str
    first_name: str | None = None
    last_name: str | None = None
    categories: tuple[CategoryOption, ...] = ()

    @field_validator("first_name", "last_name", mode="after")
    @classmethod
    def blank_is_none(cls, value: str | None) -> str | None:
        return value or None

    @property
    def full_name(self) -> str | None:
        parts = [part for part in (self.first_name, self.last_name) if part]
        return " ".join(parts) or None

    @property
    def display_name(self) -> str:
        return self.full_name or FALLBACK_NAME

    def find_category(self, name: str | None) -> CategoryOption | None:
        if not name:
            return None
        wanted = name.strip().lower()
        return next((category for category in self.categories if category.name.lower() == wanted), None)
