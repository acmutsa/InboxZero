import logging

from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from fastapi import status
from fastapi.responses import PlainTextResponse
from fastapi import Body

from pydantic import ValidationError

from redis.exceptions import RedisError
from rq import Queue

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth import outlook_pubsub_token
from app.db.schema import EmailServiceProvider
from app.db.session import get_db
from app.email_service.outlook.types.notification import OutlookNotificationList
from app.queue.redis import enqueue_outlook
from app.queue.redis import get_queue
from app.repositories.email_account import email_account_find_one_by_id

webhook_outlook_router = APIRouter(prefix="/webhooks", tags=["outlook-webhook"])
logger = logging.getLogger(__name__)


@webhook_outlook_router.post(
    "/outlook",
    status_code=status.HTTP_202_ACCEPTED,
)
def outlook_push_notification(
    body: Any = Body(None),
    validationToken: str | None = None,
    db: Session = Depends(get_db),
    queue: Queue = Depends(get_queue),
):
    if validationToken is not None:
        return PlainTextResponse(validationToken, headers={"X-Content-Type-Options": "nosniff"})
    
    try:
        notifications = OutlookNotificationList.model_validate(body).value

    except ValidationError:
        logger.warning("Ignoring malformed Outlook notification")
        return Response(status_code=status.HTTP_202_ACCEPTED)

    for notification in notifications:

        account_id = outlook_pubsub_token.decode(notification.clientState or "")

        if account_id is None:
            logger.warning("Ignoring Outlook notification with an invalid client state", extra={"subscription_id": notification.subscriptionId})
            continue

        if notification.message_id is None:
            logger.warning("Ignoring Outlook notification without a message id", extra={"subscription_id": notification.subscriptionId})
            continue

        try:
            account = email_account_find_one_by_id(db, account_id)
  
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Could not look up the email account.")

        if account is None:
            logger.info("Ignoring Outlook notification for an unknown account", extra={"subscription_id": notification.subscriptionId})
            continue

        if account.provider != EmailServiceProvider.outlook:
            logger.warning("Ignoring Outlook notification for an account that is not Outlook", extra={"account_id": str(account.id)})
            continue

        try:
            enqueue_outlook("app.jobs.outlook_sync.sync_outlook_job", queue, account_id, notification.message_id)

        except RedisError:
            logger.exception("Could not enqueue Outlook sync", extra={"account_id": str(account_id)})
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Could not enqueue the Outlook notification.")

    return Response(status_code=status.HTTP_202_ACCEPTED)
