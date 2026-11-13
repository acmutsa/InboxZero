import base64
import binascii
import json
import logging
import uuid

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from pydantic import ValidationError

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth import pubsub_token
from app.db.schema import EmailServiceProvider
from app.db.session import get_db
from app.email_service.gmail.types.notification import GmailNotification
from app.models.pubsub_push_request import PubSubPushRequest
from app.repositories.email_account import email_account_find_one_active_by_email

webhook_gmail_router = APIRouter(prefix="/webhooks", tags=["gmail-webhook"])
logger = logging.getLogger(__name__)


@webhook_gmail_router.post(
    "/gmail",
    status_code=status.HTTP_200_OK,
)
def gmail_push_notification(
    body: PubSubPushRequest,
    pubsub_token: None = Depends(pubsub_token.decrypt),
    db: Session = Depends(get_db),


):
    notification = decode_gmail_notification(body)

    if notification is None:
        return

    try:
        account = email_account_find_one_active_by_email(db, notification.emailAddress)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Could not look up the email account.")

    if account is None:
        logger.info("Ignoring Gmail notification for an unknown account", extra={"pubsub_message_id": body.message.messageId})
        return

    if account.provider != EmailServiceProvider.gmail:
        logger.warning("Ignoring Gmail notification for an account that is not Gmail", extra={"pubsub_message_id": body.message.messageId, "account_id": str(account.id)})
        return

    #enqueue_gmail_sync(account.id, notification.historyId)


def decode_gmail_notification(body: PubSubPushRequest) -> GmailNotification | None:
    if body.message.data is None:
        logger.warning("Ignoring Pub/Sub message without data", extra={"pubsub_message_id": body.message.messageId})
        return None

    try:
        payload = json.loads(base64.b64decode(body.message.data, validate=True))
        return GmailNotification.model_validate(payload)

    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError, ValidationError):
        logger.warning("Ignoring malformed Gmail notification", extra={"pubsub_message_id": body.message.messageId})
        return None