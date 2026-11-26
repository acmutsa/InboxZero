import uuid

from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.db.schema import Email
from app.db.schema import EmailAccount


def create_email(
    db: Session,
    email_account_id: uuid.UUID,
    provider_message_id: str,
    from_address: str,
    subject: str | None,
    body: str | None,
) -> uuid.UUID | None:
    statement = (
        insert(Email)
        .values(
            email_account_id=email_account_id,
            provider_message_id=provider_message_id,
            from_address=from_address,
            subject=subject,
            body=body,
        )
        .on_conflict_do_nothing(constraint="uq_emails_email_account_id_provider_message_id")
        .returning(Email.id)
    )
    return db.scalar(statement)


def email_find_one_by_email_id(
    db: Session,
    email_id: uuid.UUID,
) -> Email | None:
    return db.get(Email, email_id)


def email_set_category(
    db: Session,
    email_id: uuid.UUID,
    category_id: uuid.UUID,
) -> None:
    db.execute(update(Email).where(Email.id == email_id).values(category_id=category_id))


def emails_find_all_by_user(
    db: Session,
    user_id: uuid.UUID,
) -> list[Email]:
    return list(db.scalars(
        select(Email)
        .join(EmailAccount, Email.email_account_id == EmailAccount.id)
        .where(EmailAccount.user_id == user_id, EmailAccount.deleted_at.is_(None))
        .options(selectinload(Email.category))
        .order_by(Email.created_at.desc())
    ))
