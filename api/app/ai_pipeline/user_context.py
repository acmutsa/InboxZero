"""Who the pipeline is working for, loaded from the database for each email."""

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import field_validator

# Used in prompts when the user has no name stored.
FALLBACK_NAME = "user"


class UserContext(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    # The connected mailbox address (email_accounts.email_account).
    email: str
    first_name: str | None = None
    last_name: str | None = None

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
        """Full name if stored, otherwise the generic "user"."""
        return self.full_name or FALLBACK_NAME
