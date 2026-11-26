import uuid

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.db.schema import Draft
from app.db.schema import DraftStatus
from app.db.schema import Email
from app.db.schema import EmailAccount


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


def drafts_find_all_by_user(
    db: Session,
    user_id: uuid.UUID,
    status: DraftStatus,
) -> list[Draft]:
    return list(db.scalars(
        select(Draft)
        .join(EmailAccount, Draft.email_account_id == EmailAccount.id)
        .where(EmailAccount.user_id == user_id, EmailAccount.deleted_at.is_(None), Draft.status == status)
        .order_by(Draft.updated_at.desc())
    ))


def draft_find_one_by_id_and_user_id(
    db: Session,
    draft_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Draft | None:
    return db.scalar(
        select(Draft)
        .join(EmailAccount, Draft.email_account_id == EmailAccount.id)
        .where(Draft.id == draft_id, EmailAccount.user_id == user_id, EmailAccount.deleted_at.is_(None))
    )


def draft_update(
    db: Session,
    draft: Draft,
    body: str | None,
    status: DraftStatus | None,
) -> Draft | None:
    """Update a draft that is still in review; None if it was approved meanwhile."""
    values = {key: value for key, value in {"body": body, "status": status}.items() if value is not None}
    # Conditional UPDATE so two approves at once can't both win.
    updated = db.execute(
        update(Draft)
        .where(Draft.id == draft.id, Draft.status == DraftStatus.in_review)
        .values(**values, updated_at=func.now())
    ).rowcount
    if not updated:
        return None
    db.refresh(draft)
    return draft
