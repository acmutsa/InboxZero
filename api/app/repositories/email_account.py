from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.schema import EmailAccount
from app.db.schema import EmailServiceProvider
from app.db.schema import User


def get_email_account(
    db: Session, 
    email: str
) -> EmailAccount | None:
    return db.scalar(select(EmailAccount).where(EmailAccount.email_account == email.lower(), EmailAccount.deleted_at.is_(None)))

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
