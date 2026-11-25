import logging
import uuid

from email.utils import formataddr

from redis.exceptions import RedisError

from app.db.schema import EmailServiceProvider
from app.db.session import SessionLocal
from app.email_service.outlook.outlook import OutlookService
from app.email_service.outlook.token_manager import OutlookTokenManager
from app.email_service.outlook.types.error import OutlookServiceError
from app.email_service.outlook.types.message import Message
from app.email_service.outlook.types.message_request import MessageRequest
from app.queue.redis import draft_queue
from app.queue.redis import enqueue_draft_email
from app.repositories.email import create_email
from app.repositories.email_account import email_account_find_one_by_id

logger = logging.getLogger(__name__)


def sync_outlook_job(account_id: str, message_id: str) -> None:
    email_id = _save_new_email(uuid.UUID(account_id), message_id)

    if email_id is None:
        return

    try:
        enqueue_draft_email(draft_queue, email_id)
    except RedisError:
        logger.exception("Could not enqueue saved email for processing", extra={"account_id": account_id, "email_id": str(email_id)})

    logger.info("Outlook sync finished", extra={"account_id": account_id, "email_id": str(email_id)})


def _save_new_email(account_id: uuid.UUID, message_id: str) -> uuid.UUID | None:
    with SessionLocal() as db:
        account = email_account_find_one_by_id(db, account_id)

        if account is None:
            logger.info("Skipping Outlook sync for a missing or disconnected account", extra={"account_id": str(account_id)})
            return None

        if account.provider != EmailServiceProvider.outlook:
            logger.warning("Skipping Outlook sync for an account that is not Outlook", extra={"account_id": str(account_id)})
            return None

        outlook = OutlookService(OutlookTokenManager(account))
        message = _get_message_or_none(outlook, message_id)

        if message is None or message.isDraft:
            return None

        email_id = create_email(
            db,
            email_account_id=account.id,
            provider_message_id=message.id,
            from_address=_sender(message),
            subject=message.subject,
            body=message.text,
        )
        db.commit()

    return email_id


def _get_message_or_none(outlook: OutlookService, message_id: str) -> Message | None:
    try:
        return outlook.get_message(MessageRequest(id=message_id))
    except OutlookServiceError as error:
        if error.status_code == 404:
            logger.info("Outlook message was deleted before it could be synced", extra={"outlook_message_id": message_id})
            return None
        raise


def _sender(message: Message) -> str:
    if message.from_user is None or not message.from_user.emailAddress.address:
        return ""
    sender = message.from_user.emailAddress
    return formataddr((sender.name or "", sender.address))
