import uuid

from datetime import datetime
from datetime import timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.schema import EmailAccount
from app.db.schema import EmailServiceProvider
from app.db.schema import User

def email_account_find_one_by_email(
    db: Session,
    email: str,
    user_id: uuid.UUID
) -> EmailAccount | None:
    return db.scalar(select(EmailAccount).where(EmailAccount.email_account == email, EmailAccount.user_id == user_id, EmailAccount.deleted_at.is_(None)))

def email_account_find_one_active_by_email(
    db: Session,
    email: str,
) -> EmailAccount | None:
    return db.scalar(select(EmailAccount).where(EmailAccount.email_account == email.lower(), EmailAccount.deleted_at.is_(None)))

def email_account_find_one_by_id(
    db: Session,
    email_id: uuid.UUID,
    user_id: uuid.UUID
) -> EmailAccount | None:
    return db.scalar(select(EmailAccount).where(EmailAccount.id == email_id, EmailAccount.user_id == user_id, EmailAccount.deleted_at.is_(None)))

def email_accounts_find_all_by_user(
    db: Session,
    user_id: uuid.UUID
) -> list[EmailAccount]:
    return list(db.scalars(select(EmailAccount).where(EmailAccount.user_id == user_id, EmailAccount.deleted_at.is_(None)).order_by(EmailAccount.created_at)))

def create_email_account(
    db: Session,
    user: User,
    email: str,
    provider: EmailServiceProvider,
) -> EmailAccount:
    account = EmailAccount(
        user=user,
        email_account=email.lower(),
        provider=provider
    )
    db.add(account)
    db.flush()
    return account

def email_account_disconnect(
    db: Session,
    account: EmailAccount
) -> None:
    account.deleted_at = datetime.now(timezone.utc)
    account.token = None
    db.flush()