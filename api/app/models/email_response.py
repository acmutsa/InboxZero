import uuid
from datetime import datetime
from pydantic import BaseModel

from app.db.schema import Email


class EmailResponse(BaseModel):
    id: uuid.UUID
    email_account_id: uuid.UUID
    from_address: str
    subject: str | None = None
    body: str | None = None
    category: str | None = None
    created_at: datetime

    @classmethod
    def from_email(cls, email: Email) -> "EmailResponse":
        return cls(
            id=email.id,
            email_account_id=email.email_account_id,
            from_address=email.from_address,
            subject=email.subject,
            body=email.body,
            category=email.category.category_name if email.category else None,
            created_at=email.created_at,
        )
