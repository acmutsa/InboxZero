
import secrets
import time
import requests

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from pydantic import BaseModel

from app.auth.jwt import decode
from app.models.decoded_jwt import DecodedJWT
from app.models.autorization_url import AuthorizationUrl

from app.email_service.outlook.oauth import MicrosoftOAuth


auth_outlook_router = APIRouter(
    prefix="/auth/outlook",
    tags=["outlook-connect"],
)

# Temporary local-development storage.
# Replace with a shared store and database token cache.
pending_logins = {}
connected_accounts = {}


class OutlookCallbackRequest(BaseModel):
    state: str
    code: str


@auth_outlook_router.post(
    "/connect-outlook",
    response_model=AuthorizationUrl,
)
def connect_outlook(
    decoded_jwt: DecodedJWT = Depends(decode),
    oauth: MicrosoftOAuth = Depends(MicrosoftOAuth),
):
    state = secrets.token_urlsafe(32)

    pending_logins[state] = {
        "user_id": decoded_jwt.user_id,
        "created_at": time.time(),
    }

    url = oauth.get_authorization_url(state)

    return AuthorizationUrl(
        authorization_url=url
    )



@auth_outlook_router.get("/callback")
def callback(
    code: str,
    state: str,
    oauth: MicrosoftOAuth = Depends(MicrosoftOAuth),
):
    # Validate and consume the saved OAuth state
    login = pending_logins.pop(state, None)

    if not login:
        raise HTTPException(
            status_code=400,
            detail="Invalid or already used login state",
        )

    if time.time() - login["created_at"] > 600:
        raise HTTPException(
            status_code=400,
            detail="Outlook login has expired",
        )

    user_id = login["user_id"]

    try:
        result = oauth.exchange_code(code)
        email = oauth.get_verified_email(
            result["access_token"]
        )

    except (RuntimeError, ValueError) as error:
        raise HTTPException(
            status_code=400,
            detail="Microsoft authentication failed",
        ) from error

    except requests.RequestException as error:
        raise HTTPException(
            status_code=502,
            detail="Microsoft account verification failed",
        ) from error

    # Temporary development-only storage
    connected_accounts[user_id] = {
        "email": email,
        "access_token": result["access_token"],
        "expires_at": time.time() + result.get(
            "expires_in", 3600
        ),
    }

    return {
        "status": "success",
        "message": "Outlook account connected",
        "email": email,
    }
