import logging
from typing import Annotated

import requests
from fastapi import APIRouter, Depends, HTTPException, status
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError, OAuth2Error
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import app.auth.google_state_jwt as google_state_jwt
from app.auth.jwt import decode
from app.db.session import get_db

auth_gmail_router = APIRouter(prefix="/auth/google", tags=["gmail-connect"])
logger = logging.getLogger(__name__)


@auth_gmail_router.post(
    "/connect-gmail",
    response_model=AuthorizationUrl,
    status_code=status.HTTP_200_OK,
)
def connect_gmail(
    oauth: OAuth,
    body: ConnectGmailRequest , 
    decoded_jwt: DecodedJWT = Depends(decode), 
):
    state = google_state_jwt.encode(decoded_jwt["sub"], body.gmail)
    url = oauth.get_authorization_url(state=state, gmail=body.gmail)
    return AuthorizationUrl(
        url=url
    )


@auth_gmail_router.post(
    "/callback",
    status_code=status.HTTP_200_OK,
)
def callback(
    oauth: OAuth,
    body: GmailCallbackRequest,
    decoded_jwt: DecodedJWT = Depends(decode),
    db: Session = Depends(get_db)
):
    user_id = decoded_jwt["sub"]
    state = google_state_jwt.decode(body.state, user_id)

    try:

        credentials = oauth.exchange_code(body.state, body.code)

    except InvalidGrantError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="This sign-in link was already used or expired. Please connect Gmail again.",
        )

    except OAuth2Error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Gmail connection isn't available right now. Please try again later.",
        )

    except requests.RequestException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="We couldn't reach Google. Please try again.",
        )

    try:
        email = oauth.get_verified_email(credentials)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="We couldn't verify your Google account. Please try again.",
        )

    if email.lower() != state["gmail"].lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"You signed in as {email}, expected {state['gmail']}"
        )

    try:
    # Save to DB, encrypting the refresh token
    except Exception:
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save Gmail. Please try again later.",
            )

    return {
        "email": email, 
        "connected": True
    }
