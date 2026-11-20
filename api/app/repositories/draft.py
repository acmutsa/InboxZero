import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.schema import Draft
from app.db.schema import Email


def draft_find_one_by_id(
    db: Session,
    draft_id: uuid.UUID,
) -> Draft | None:
    return db.get(Draft, draft_id)


def draft_find_one_by_email_id(
    db: Session,
    email_id: uuid.UUID,
) -> Draft | None:
    return db.scalar(select(Draft).where(Draft.reply_to_email == email_id).limit(1))


def draft_create_for_email(
    db: Session,
    email: Email,
    to_address: str,
    subject: str | None,
    body: str | None,
) -> Draft:
    """Add a reply draft for `email`. The caller commits."""
    draft = Draft(
        email_account_id=email.email_account_id,
        category_id=email.category_id,
        reply_to_email=email.id,
        to_address=to_address,
        subject=subject,
        body=body,
    )
    db.add(draft)
    db.flush()
    return draft
