from datetime import datetime

from sqlalchemy.orm import Session

from app.auth.refresh_token import encrypt

from app.db.schema import EmailAccount
from app.db.schema import EmailAccountToken


def create_tokens(
    db: Session,
    account: EmailAccount,
    authentication_token: str,
    refresh_token: str,
    expires_at: datetime | None,
) -> EmailAccountToken:
    token = EmailAccountToken(
        authentication_token=encrypt(authentication_token),
        refresh_token=encrypt(refresh_token),
        expires_at=expires_at,
    )
    account.token = token
    db.flush()
    return token


def update_tokens(
    db: Session,
    account: EmailAccount,
    authentication_token: str,
    expires_at: datetime | None,
    refresh_token: str | None = None,
) -> None:
    token = account.token
    token.authentication_token = encrypt(authentication_token)
    token.expires_at = expires_at

    if refresh_token is not None:
        token.refresh_token = encrypt(refresh_token)

    db.flush()
