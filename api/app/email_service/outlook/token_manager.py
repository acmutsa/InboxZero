import logging
import uuid

from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Any

import requests

from app.auth.refresh_token import decrypt
from app.config import config
from app.db.schema import EmailAccount
from app.db.session import SessionLocal
from app.email_service.outlook.oauth import MicrosoftOAuth
from app.email_service.outlook.types.error import OutlookServiceError
from app.repositories.email_account import email_account_find_one_by_email_id_and_user_id
from app.repositories.email_account_token import update_tokens

logger = logging.getLogger(__name__)

REFRESH_BEFORE_EXPIRY = timedelta(minutes=5)
DEFAULT_LIFETIME_SECONDS = 3600


class OutlookSession(requests.Session):
    def __init__(self, token_manager: "OutlookTokenManager") -> None:
        super().__init__()
        self._token_manager = token_manager

    def request(self, method: str, url: str, headers: dict[str, str] | None = None, **kwargs: Any) -> requests.Response:
        access_token = self._token_manager.get_access_token()
        response = self._send(method, url, access_token, headers, **kwargs)

        if self._was_rejected(response) and self._token_manager.can_refresh:
            new_access_token = self._token_manager.get_access_token(force_refresh=True)
            response = self._send(method, url, new_access_token, headers, **kwargs)

        return response

    def _send(self, method: str, url: str, access_token: str, headers: dict[str, str] | None, **kwargs: Any) -> requests.Response:
        headers_with_token = {**(headers or {}), "Authorization": f"Bearer {access_token}"}
        return super().request(method, url, headers=headers_with_token, **kwargs)

    @staticmethod
    def _was_rejected(response: requests.Response) -> bool:
        return response.status_code == 401


class OutlookTokenManager:
    _account_id: uuid.UUID | None = None
    _user_id: uuid.UUID | None = None
    _oauth: MicrosoftOAuth | None = None
    _http_session: OutlookSession | None = None

    access_token: str
    refresh_token: str | None = None
    expires_at: datetime | None = None

    def __init__(self, account: EmailAccount, oauth: MicrosoftOAuth | None = None) -> None:
        self._account_id = account.id
        self._user_id = account.user_id
        self._oauth = oauth or MicrosoftOAuth()

        self.access_token = decrypt(account.token.authentication_token)
        self.refresh_token = decrypt(account.token.refresh_token)
        self.expires_at = self._to_aware_utc(account.token.expires_at)

    @classmethod
    def from_access_token(cls, access_token: str) -> "OutlookTokenManager":
        manager = cls.__new__(cls)
        manager.access_token = access_token
        return manager

    @property
    def can_refresh(self) -> bool:
        return self.refresh_token is not None

    def get_session(self) -> OutlookSession:
        if self._http_session is None:
            self._http_session = OutlookSession(self)
        return self._http_session

    def get_access_token(self, force_refresh: bool = False) -> str:
        needs_refresh = force_refresh or self._expires_soon()

        if self.can_refresh and needs_refresh:
            self._refresh()

        return self.access_token

    def _expires_soon(self) -> bool:
        if self.expires_at is None:
            return True

        refresh_at = self.expires_at - REFRESH_BEFORE_EXPIRY
        return datetime.now(timezone.utc) >= refresh_at

    def _refresh(self) -> None:
        tokens = self._request_new_tokens()
        previous_refresh_token = self.refresh_token
        lifetime = timedelta(seconds=int(tokens.get("expires_in", DEFAULT_LIFETIME_SECONDS)))

        self.access_token = tokens["access_token"]
        self.refresh_token = tokens.get("refresh_token") or previous_refresh_token
        self.expires_at = datetime.now(timezone.utc) + lifetime

        refresh_token_changed = self.refresh_token != previous_refresh_token
        self._save_tokens(new_refresh_token=self.refresh_token if refresh_token_changed else None)

    def _request_new_tokens(self) -> dict[str, Any]:
        try:
            tokens = self._oauth.app.acquire_token_by_refresh_token(self.refresh_token, scopes=config.OUTLOOK_SCOPES)

        except requests.RequestException as error:
            raise OutlookServiceError("Could not reach Microsoft to refresh Outlook access.", status_code=503) from error

        if "access_token" not in tokens:
            logger.warning("Outlook token refresh failed", extra={"account_id": str(self._account_id), "error": tokens.get("error")})
            raise OutlookServiceError("Outlook access was revoked or expired. Please connect Outlook again.", status_code=401)

        return tokens

    def _save_tokens(self, new_refresh_token: str | None) -> None:
        try:
            with SessionLocal() as db:
                account = email_account_find_one_by_id(db, self._account_id)

                if account is None or account.token is None:
                    return

                update_tokens(
                    db,
                    account,
                    authentication_token=self.access_token,
                    expires_at=self.expires_at,
                    refresh_token=new_refresh_token,
                )
                db.commit()

        except Exception:
            logger.warning("Could not save refreshed Outlook token", extra={"account_id": str(self._account_id)}, exc_info=True)

    @staticmethod
    def _to_aware_utc(value: datetime | None) -> datetime | None:
        if value is None:
            return None

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value
