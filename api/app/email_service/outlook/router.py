import logging
import requests

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.autorization_url import AuthorizationUrl
from app.models.connect_outlook_request import ConnectOutlookRequest
from app.models.decoded_jwt import DecodedJWT
from app.models.outlook_callback_request import OutlookCallbackRequest

from app.auth import outlook_state_jwt
from app.auth.jwt import decode

from app.db.schema import EmailServiceProvider
from app.db.session import get_db

from app.email_service.outlook.oauth import MicrosoftOAuth
from app.email_service.outlook.outlook import OutlookService
from app.email_service.outlook.token_manager import OutlookTokenManager
from app.email_service.outlook.types.error import OutlookServiceError

from app.repositories.email_account import create_email_account
from app.repositories.email_account import email_account_find_one_by_email_and_user_id
from app.repositories.email_account_token import create_tokens
from app.repositories.user import user_find_one_by_clerk_id

auth_outlook_router = APIRouter(prefix="/auth/outlook")
logger = logging.getLogger(__name__)


@auth_outlook_router.post(
    "/connect-outlook",
    response_model=AuthorizationUrl,
    status_code=status.HTTP_200_OK,
)
def connect_outlook(
    body: ConnectOutlookRequest,
    decoded_jwt: DecodedJWT = Depends(decode),
    oauth: MicrosoftOAuth = Depends(MicrosoftOAuth),
):
    state = outlook_state_jwt.encode(decoded_jwt.user_id, body.outlook)
    url = oauth.get_authorization_url(state=state, outlook=body.outlook)

    return AuthorizationUrl(
        authorization_url=url
    )

@auth_outlook_router.post(
    "/callback",
    status_code=status.HTTP_200_OK,
)
def callback(
    body: OutlookCallbackRequest,
    decoded_jwt: DecodedJWT = Depends(decode),
    oauth: MicrosoftOAuth = Depends(MicrosoftOAuth),
    db: Session = Depends(get_db)
):
    user_id = decoded_jwt.user_id
    state = outlook_state_jwt.decode(body.state, user_id)

    try:
        tokens = oauth.exchange_code(body.code)

    except OutlookServiceError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="This sign-in link was already used or expired. Please connect Outlook again.",
        )

    except requests.RequestException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="We couldn't reach Microsoft. Please try again.",
        )

    try:
        email = OutlookService(OutlookTokenManager.from_access_token(tokens["access_token"])).get_verified_email()

    except (ValueError, OutlookServiceError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="We couldn't verify your Microsoft account. Please try again.",
        )

    if email.lower() != state.outlook.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"You signed in as {email}, expected {state.outlook}"
        )

    if not tokens.get("refresh_token"):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Microsoft didn't grant offline access. Please connect Outlook again.",
        )

    expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(tokens.get("expires_in", 3600)))

    try:
        user = user_find_one_by_clerk_id(db, user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account not found. Please create an account first.",
            )

        email_account = email_account_find_one_by_email_and_user_id(db, email.lower(), user.id)

        if email_account is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="This Outlook account is already connected.",
            )

        account = create_email_account(db, user, email, EmailServiceProvider.outlook)
        create_tokens(db, account, tokens["access_token"], tokens["refresh_token"], expires_at)
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="This Outlook account is already connected.",
        )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save Outlook. Please try again later.",
        )

    return {
        "email": email,
        "connected": True
    }
