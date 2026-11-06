
from datetime import datetime, timedelta, timezone

from app.email_service.outlook.oauth import MicrosoftOAuth


class OutlookTokenManager:
    """
    Handles Microsoft token expiration and refresh.

    Database storage is intentionally handled separately
    so this class can be tested without PostgreSQL.
    """

    REFRESH_BUFFER_SECONDS = 300

    def __init__(self, oauth=None):
        self.oauth = oauth or MicrosoftOAuth()

    @staticmethod
    def now():
        return datetime.now(timezone.utc)

    def is_expired(self, expires_at: datetime) -> bool:
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        refresh_time = expires_at - timedelta(
            seconds=self.REFRESH_BUFFER_SECONDS
        )

        return self.now() >= refresh_time

    def refresh(self, refresh_token: str) -> dict:
        result = self.oauth.refresh_access_token(refresh_token)

        access_token = result.get("access_token")

        if not access_token:
            raise RuntimeError(
                "Microsoft did not return an access token"
            )

        expires_in = int(result.get("expires_in", 3600))

        if expires_in <= 0:
            raise RuntimeError(
                "Microsoft returned an invalid token lifetime"
            )

        return {
            "access_token": access_token,
            "refresh_token": result.get("refresh_token")
                or refresh_token,
            "expires_at": self.now() + timedelta(
                seconds=expires_in
            ),
        }

    def get_valid_token(
        self,
        access_token: str,
        refresh_token: str,
        expires_at: datetime,
    ) -> dict:
        if not self.is_expired(expires_at):
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at,
                "refreshed": False,
            }

        updated = self.refresh(refresh_token)
        updated["refreshed"] = True

        return updated
