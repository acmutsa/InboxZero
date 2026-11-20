
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.schema import EmailServiceProvider
from app.repositories.user import user_find_one_by_clerk_id
from app.repositories.email_account import (
    create_email_account,
    email_account_find_one_by_email,
    email_account_find_one_active_by_email,
)
from app.repositories.email_account_token import (
    create_tokens,
    update_tokens,
)
from app.email_service.outlook.account_store import OutlookCredentials


class DatabaseOutlookAccountStore:
    def __init__(self, db: Session):
        self.db = db

    def save(self, account: OutlookCredentials) -> None:
        try:
            user = user_find_one_by_clerk_id(
                self.db,
                account.user_id,
            )

            if user is None:
                raise ValueError("InboxZero user not found")

            existing = email_account_find_one_by_email(
                self.db,
                account.email.lower(),
                user.id,
            )

            if existing is None:
                other_account = email_account_find_one_active_by_email(
                    self.db,
                    account.email,
                )

                if other_account is not None:
                    raise ValueError(
                        "This email address is already connected"
                    )

                existing = create_email_account(
                    db=self.db,
                    user=user,
                    email=account.email,
                    provider=EmailServiceProvider.outlook,
                )

            elif existing.provider != EmailServiceProvider.outlook:
                raise ValueError(
                    "This email belongs to another provider"
                )

            if existing.token is None:
                create_tokens(
                    db=self.db,
                    account=existing,
                    authentication_token=account.access_token,
                    refresh_token=account.refresh_token,
                    expires_at=account.expires_at,
                )
            else:
                update_tokens(
                    db=self.db,
                    account=existing,
                    authentication_token=account.access_token,
                    refresh_token=account.refresh_token,
                    expires_at=account.expires_at,
                )

            self.db.commit()

        except Exception:
            self.db.rollback()
            raise
