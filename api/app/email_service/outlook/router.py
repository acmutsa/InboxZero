
import secrets
import time
import requests

from fastapi import APIRouter, Depends, HTTPException

from app.auth.jwt import decode
from app.models.decoded_jwt import DecodedJWT
from app.models.autorization_url import AuthorizationUrl

from app.email_service.outlook.oauth import MicrosoftOAuth
from app.email_service.outlook.account_store import (
    InMemoryOutlookAccountStore,
)
from app.email_service.outlook.connection_service import (
    OutlookConnectionService,
)


auth_outlook_router = APIRouter(
    prefix="/auth/outlook",
    tags=["outlook-connect"],
)

# Development-only storage.
# Replace with shared storage before production deployment.
pending_logins = {}

account_store = InMemoryOutlookAccountStore()


def get_connection_service(
    oauth: MicrosoftOAuth = Depends(MicrosoftOAuth),
):
    return OutlookConnectionService(
        store=account_store,
        oauth=oauth,
    )


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
    service: OutlookConnectionService = Depends(
        get_connection_service
    ),
):
    # Consume the OAuth state exactly once.
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
        result = service.connect(
            user_id=user_id,
            code=code,
        )

    except (RuntimeError, ValueError, KeyError) as error:
        raise HTTPException(
            status_code=400,
            detail="Microsoft authentication failed",
        ) from error

    except requests.RequestException as error:
        raise HTTPException(
            status_code=502,
            detail="Microsoft account verification failed",
        ) from error

    return {
        "status": "success",
        "message": "Outlook account connected",
        "email": result["email"],
    }
