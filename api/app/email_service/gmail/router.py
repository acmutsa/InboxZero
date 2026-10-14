import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import decode_access_token
from app.db.session import get_db

auth_gmail_router = APIRouter(prefix="/auth/google", tags=["gmail-connect"])
logger = logging.getLogger(__name__)


@auth_gmail_router.post(
    "/connect-gmail",
    response_model=AuthorizationUrl,
    status_code=status.HTTP_200_OK,
)
async def connect_gmail(
    oauth: OAuth,
    body: ConnectGmailRequest, 
    decoded_jwt: DecodedJWT, 
):
    pass


@auth_gmail_router.post(
    "/callback",
    status_code=status.HTTP_200_OK,
)
async def callback(
    oauth: OAuth, 
    body: CallbackRequest, 
    decoded_jwt: DecodedJWT, 
    db: Db
):
    pass


@auth_gmail_router.delete(
    "/connected-emails/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def disconnect_email(account_id: int, decoded_jwt: DecodedJWT, db: Db):
    pass


@auth_gmail_router.get(
    "/status", 
    response_model=ConnectionStatus
    )
def connection_status(
    user_id: UserId, 
    oauth: OAuth
):
    pass


@auth_gmail_router.post(
    "/logout", 
    status_code=status.HTTP_204_NO_CONTENT
)
def logout(user_id: UserId, oauth: OAuth):
    pass
