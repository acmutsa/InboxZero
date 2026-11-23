from typing import Annotated

from fastapi import Header
from fastapi import HTTPException
from fastapi import status

from google.auth.exceptions import GoogleAuthError
from google.auth.exceptions import TransportError
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.config import config


def decrypt(
    authorization: Annotated[str | None, Header()] = None,
) -> None:

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Pub/Sub token.",
        )

    token = authorization.split(" ", 1)[1]

    try:
        claims = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            audience=config.GMAIL_PUBSUB_AUDIENCE,
        )

    except TransportError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Could not verify the Pub/Sub token right now.")

    except (ValueError, GoogleAuthError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Pub/Sub token.")

    if claims.get("email") != config.GMAIL_PUBSUB_SERVICE_ACCOUNT or not claims.get("email_verified"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Pub/Sub token was not issued for our subscription.")
