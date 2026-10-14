import google.oauth2.credentials
import google_auth_oauthlib.flow
from app.config import config
from app.models.connected_email import ConnectedEmail


TOKEN_URI = "https://oauth2.googleapis.com/token"
REVOKE_URI = "https://oauth2.googleapis.com/revoke"
STATE_TTL_SECONDS = 600


class OAuth():

    def _get_flow() -> Flow:
        return Flow.from_client_secrets_file(
            config.get_google_client_config,
            scopes=config.get_scopes,
            redirect_uri=config.GOOGLE_REDIRECT_URI,
            autogenerate_code_verifier=False,
        )

    def get_authorization_url(clerk_id: str, gmail: str) -> str:
        authorization_url, state = _get_flow().authorization_url(
            access_type="offline",
            login_hint=gmail,
            prompt="consent", 
        )
        return authorization_url


    