from google.auth.transport import requests 
from google.oauth2 import id_token
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

from app.config import config

class GoogleOAuth:

    def _get_flow(self, state: str) -> Flow:
        flow = Flow.from_client_config(
            config.get_google_client_config,
            scopes=config.SCOPES, 
            redirect_uri=config.GOOGLE_REDIRECT_URI,
            state=state,
            autogenerate_code_verifier=False,
        )
        return flow

    def get_authorization_url(self, state: str, gmail: str) -> str:
        url, _ = self._get_flow(state).authorization_url(
            access_type="offline",
            login_hint=gmail,
            prompt="consent", 
        )
        return url

    def exchange_code(self, state: str, code: str) -> Credentials:
        flow = self._get_flow(state)
        flow.fetch_token(code=code)
        return flow.credentials

    def get_verified_email(self, credentials: Credentials) -> str:
        info = id_token.verify_oauth2_token(
            credentials.id_token, requests.Request(), config.GOOGLE_CLIENT_ID
        )
        return info["email"]