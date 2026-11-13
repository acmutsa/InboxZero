import logging
import uuid

from datetime import datetime
from datetime import timezone
from typing import Any

from google.auth.transport import Request
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session

from app.auth.refresh_token import decrypt
from app.config import config
from app.db.schema import EmailAccount
from app.db.session import SessionLocal
from app.email_service.gmail.types.error import GmailServiceError
from app.repositories.email_account_token import update_tokens

logger = logging.getLogger(__name__)

class CredentialsWithRefreshHook(Credentials):

    def __init__(self, *, on_refresh, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._on_refresh = on_refresh

    def refresh(self, request: Request) -> None:
        super().refresh(request)
        if self._on_refresh is not None:
            self._on_refresh(self)


class GmailTokenManager:

    def __init__(self, account: EmailAccount) -> None:
        self._account_id: uuid.UUID = account.id
        self.credentials: Credentials = self._build_credentials(account)
        self._http_session: AuthorizedSession | None = None

    def get_session(self) -> AuthorizedSession:
        if self._http_session is None:
            self._http_session = AuthorizedSession(self.credentials)
        return self._http_session

    def _build_credentials(self, account: EmailAccount) -> Credentials:
        if account.token is None:
            raise GmailServiceError("This Gmail account has no stored tokens. Please connect Gmail again.", status_code=401)

        return CredentialsWithRefreshHook(
            token=decrypt(account.token.authentication_token),
            refresh_token=decrypt(account.token.refresh_token),
            token_uri=config.GOOGLE_TOKEN_URI,
            client_id=config.GOOGLE_CLIENT_ID,
            client_secret=config.GOOGLE_CLIENT_SECRET,
            scopes=config.SCOPES,
            expiry=self._to_naive_utc(token.expires_at),
            on_refresh=self._save_tokens,
        )

    def _save_tokens(self) -> None:
        try:
            with SessionLocal() as db:
                account = email_account_find_one_by_id(db, self._account_id, self._user_id)

                if account is None:
                    return 

                if account.token is None: 
                    return

                stored_refresh_token = decrypt(account.token.refresh_token)
                new_refresh_token = self.credentials.refresh_token if self.credentials.refresh_token != stored_refresh_token else None

                update_tokens(db, account, authentication_token=self.credentials.token, expires_at=self._to_aware_utc(self.credentials.expiry), refresh_token=new_refresh_token)
                db.commit()

        except Exception:
            logger.warning("Could not save refreshed Gmail token", extra={"account_id": str(self._account_id)}, exc_info=True)

    @staticmethod
    def _to_naive_utc(value: datetime | None) -> datetime | None:
        if value is None: return None
        if value.tzinfo is not None:
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    @staticmethod
    def _to_aware_utc(value: datetime | None) -> datetime | None:
        if value is None: return None
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
