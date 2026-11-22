import logging
import msal
import requests

from app.config import config

logger = logging.getLogger(__name__)


class MicrosoftOAuth:

    GRAPH_URL = "https://graph.microsoft.com/v1.0"

    def __init__(self):
        self.app = msal.ConfidentialClientApplication(
            client_id=config.OUTLOOK_CLIENT_ID,
            client_credential=config.OUTLOOK_CLIENT_SECRET,
            authority=config.OUTLOOK_AUTHORITY,
        )

    def get_authorization_url(self, state: str, outlook: str) -> str:
        return self.app.get_authorization_request_url(
            scopes=config.OUTLOOK_SCOPES,
            state=state,
            redirect_uri=config.OUTLOOK_REDIRECT_URI,
            login_hint=outlook,
            prompt="select_account",
        )

    def exchange_code(self, code: str) -> dict:
        result = self.app.acquire_token_by_authorization_code(
            code=code,
            scopes=config.OUTLOOK_SCOPES,
            redirect_uri=config.OUTLOOK_REDIRECT_URI,
        )

        if "access_token" not in result:
            # Log only the error category, never tokens or codes.
            logger.warning("Microsoft OAuth error: %s %s", result.get("error"), result.get("error_codes"))
            raise RuntimeError("Microsoft token exchange failed")

        return result

    def refresh_access_token(self, refresh_token: str) -> dict:
        if not refresh_token:
            raise ValueError("Microsoft refresh token is missing")

        result = self.app.acquire_token_by_refresh_token(
            refresh_token=refresh_token,
            scopes=config.OUTLOOK_SCOPES,
        )

        if "access_token" not in result:
            raise RuntimeError(
                "Microsoft token refresh failed: "
                + result.get("error", "unknown_error")
            )

        return result

    def get_verified_email(self, access_token: str) -> str:
        response = requests.get(
            f"{self.GRAPH_URL}/me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=config.OUTLOOK_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        user = response.json()

        email = user.get("mail") or user.get("userPrincipalName")

        if not email:
            raise ValueError("Microsoft did not return an email address")

        return email
