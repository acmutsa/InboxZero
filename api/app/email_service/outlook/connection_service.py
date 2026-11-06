
from datetime import datetime, timedelta, timezone

from app.email_service.outlook.account_store import (
    OutlookCredentials,
    OutlookAccountStore,
)
from app.email_service.outlook.oauth import MicrosoftOAuth


class OutlookConnectionService:
    def __init__(
        self,
        store: OutlookAccountStore,
        oauth: MicrosoftOAuth,
    ):
        self.store = store
        self.oauth = oauth

    def connect(self, user_id: str, code: str) -> dict:
        if not user_id or not code:
            raise ValueError("User ID and authorization code are required")

        tokens = self.oauth.exchange_code(code)

        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")

        if not access_token or not refresh_token:
            raise RuntimeError(
                "Microsoft did not return the required tokens"
            )

        profile = self.oauth.get_account_profile(access_token)

        expires_in = int(tokens.get("expires_in", 3600))

        if expires_in <= 0:
            raise RuntimeError("Invalid Microsoft token expiration")

        account = OutlookCredentials(
            user_id=user_id,
            microsoft_account_id=profile["microsoft_account_id"],
            email=profile["email"],
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.now(timezone.utc)
            + timedelta(seconds=expires_in),
        )

        self.store.save(account)

        return {
            "status": "success",
            "email": account.email,
            "microsoft_account_id": account.microsoft_account_id,
        }
