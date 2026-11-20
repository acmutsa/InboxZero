
import os
import msal
import requests

from dotenv import load_dotenv

load_dotenv()


class MicrosoftOAuth:
    SCOPES = [
        "User.Read",
        "Mail.ReadWrite",
        "Mail.Send",
        "MailboxSettings.ReadWrite",
    ]

    GRAPH_URL = "https://graph.microsoft.com/v1.0"

    def __init__(self):
        self.client_id = os.getenv("OUTLOOK_CLIENT_ID")
        self.client_secret = os.getenv("OUTLOOK_CLIENT_SECRET")
        self.redirect_uri = os.getenv(
            "OUTLOOK_REDIRECT_URI",
             "http://localhost:8000/auth/outlook/callback",
            )

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "OUTLOOK_CLIENT_ID and "
                "OUTLOOK_CLIENT_SECRET are required"
            )

        self.app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=(
                "https://login.microsoftonline.com/consumers"
            ),
        )

    def get_authorization_url(self, state: str) -> str:
        """Generate the Microsoft sign-in URL."""

        return self.app.get_authorization_request_url(
            scopes=self.SCOPES,
            state=state,
            redirect_uri=self.redirect_uri,
            prompt="select_account",
        )

    
    def exchange_code(self, code: str) -> dict:
        """Exchange Microsoft authorization code for tokens."""

        result = self.app.acquire_token_by_authorization_code(
            code=code,
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri,
        )

        if "access_token" not in result:
         # Log only the error category, not tokens or codes.
            print("Microsoft OAuth error:", result.get("error"))
            print("Microsoft OAuth error code:", result.get("error_codes"))

            raise RuntimeError("Microsoft token exchange failed")

        return result

    def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Exchange a Microsoft refresh token for a new access token.
        """
        if not refresh_token:
            raise ValueError("Microsoft refresh token is missing")

        result = self.app.acquire_token_by_refresh_token(
            refresh_token=refresh_token,
            scopes=self.SCOPES,
        )

        if "access_token" not in result:
            raise RuntimeError(
                "Microsoft token refresh failed: "
                + result.get("error", "unknown_error")
            )

        return result

    def get_account_profile(self, access_token: str) -> dict:
        """
        Retrieve the connected Microsoft account's ID and email.
        """
        response = requests.get(
            f"{self.GRAPH_URL}/me",
            headers={
                "Authorization": f"Bearer {access_token}"
            },
            timeout=30,
        )

        response.raise_for_status()
        profile = response.json()

        account_id = profile.get("id")
        email = (
            profile.get("mail")
            or profile.get("userPrincipalName")
        )

        if not account_id or not email:
            raise ValueError(
                "Microsoft account ID or email is missing"
            )

        return {
            "microsoft_account_id": account_id,
            "email": email,
        }


    def get_verified_email(self, access_token: str) -> str:
        """Retrieve the authenticated Microsoft account."""

        response = requests.get(
            f"{self.GRAPH_URL}/me",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            timeout=30,
        )

        response.raise_for_status()
        user = response.json()

        email = (
            user.get("mail")
            or user.get("userPrincipalName")
        )

        if not email:
            raise ValueError(
                "Microsoft did not return an email address"
            )

        return email
