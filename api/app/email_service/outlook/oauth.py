import logging
import msal
from app.config import config
from app.email_service.outlook.types.error import OutlookServiceError

logger = logging.getLogger(__name__)

class MicrosoftOAuth:

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
            raise OutlookServiceError("Microsoft token exchange failed", status_code=400)

        return result
