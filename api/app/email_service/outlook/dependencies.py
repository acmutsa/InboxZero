
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.jwt import decode
from app.auth.refresh_token import decrypt
from app.db.schema import EmailAccount, EmailServiceProvider
from app.db.session import get_db
from app.models.decoded_jwt import DecodedJWT
from app.repositories.email_account_token import update_tokens
from app.repositories.user import user_find_one_by_clerk_id

from app.email_service.outlook.service_manager import (
    OutlookServiceManager,
)


def get_outlook_service(
    decoded_jwt: DecodedJWT = Depends(decode),
    db: Session = Depends(get_db),
):
    user = user_find_one_by_clerk_id(
        db,
        decoded_jwt.user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="InboxZero user not found",
        )

    accounts = list(
        db.scalars(
            select(EmailAccount).where(
                EmailAccount.user_id == user.id,
                EmailAccount.provider == EmailServiceProvider.outlook,
                EmailAccount.deleted_at.is_(None),
            )
        )
    )

    if not accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No connected Outlook account found",
        )

    if len(accounts) > 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Multiple Outlook accounts connected; account selection required",
        )

    account = accounts[0]

    if account.token is None or account.token.expires_at is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Outlook account credentials are incomplete",
        )

    def save_refreshed_tokens(
        access_token,
        refresh_token,
        expires_at,
    ):
        try:
            update_tokens(
                db=db,
                account=account,
                authentication_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
            )
            db.commit()
        except Exception:
            db.rollback()
            raise

    manager = OutlookServiceManager(
        access_token=decrypt(account.token.authentication_token),
        refresh_token=decrypt(account.token.refresh_token),
        expires_at=account.token.expires_at,
        save_tokens=save_refreshed_tokens,
    )

    return manager.get_service()

