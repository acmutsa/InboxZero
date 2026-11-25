import logging
import uuid

from redis.exceptions import LockError
from redis.exceptions import RedisError

from app.db.schema import EmailServiceProvider
from app.db.session import SessionLocal
from app.email_service.gmail.gmail import GmailService
from app.email_service.gmail.token_manager import GmailTokenManager
from app.email_service.gmail.types.error import GmailServiceError
from app.email_service.gmail.types.history import HistoryListRequest
from app.email_service.gmail.types.message import Message
from app.email_service.gmail.types.message_list_request import MessageListRequest
from app.email_service.gmail.types.message_request import MessageRequest
from app.queue.redis import draft_queue
from app.queue.redis import enqueue_draft_email
from app.queue.redis import redis_connection
from app.repositories.email import create_email
from app.repositories.email_account import email_account_find_one_by_id

logger = logging.getLogger(__name__)

SYNC_LOCK_TIMEOUT_SECONDS = 60
SYNC_LOCK_WAIT_SECONDS = 10
SYNC_LABEL = "INBOX"
SKIPPED_LABELS = frozenset({"SENT", "DRAFT", "SPAM", "TRASH"})
FALLBACK_SYNC_MAX_MESSAGES = 25
HISTORY_PAGE_SIZE = 500


class SyncAlreadyRunningError(Exception):
    pass


def sync_gmail_job(account_id: str, history_id: int) -> None:
    lock = redis_connection.lock(
        f"gmail-sync:{account_id}",
        timeout=SYNC_LOCK_TIMEOUT_SECONDS,
        blocking_timeout=SYNC_LOCK_WAIT_SECONDS,
    )
    if not lock.acquire():
        raise SyncAlreadyRunningError(f"Gmail sync already running for account {account_id}")

    try:
        new_email_ids = _save_new_emails(uuid.UUID(account_id), history_id)
    finally:
        try:
            lock.release()
        except LockError:
            logger.warning("Gmail sync lock expired before release", extra={"account_id": account_id})

    for email_id in new_email_ids:
        try:
            enqueue_draft_email(draft_queue, email_id)
        except RedisError:
            logger.exception("Could not enqueue saved email for processing", extra={"account_id": account_id, "email_id": str(email_id)})

    logger.info("Gmail sync finished", extra={"account_id": account_id, "new_emails": len(new_email_ids)})


def _save_new_emails(account_id: uuid.UUID, notification_history_id: int) -> list[uuid.UUID]:
    with SessionLocal() as db:
        account = email_account_find_one_by_id(db, account_id)

        if account is None:
            logger.info("Skipping Gmail sync for a missing or disconnected account", extra={"account_id": str(account_id)})
            return []

        if account.provider != EmailServiceProvider.gmail:
            logger.warning("Skipping Gmail sync for an account that is not Gmail", extra={"account_id": str(account_id)})
            return []

        gmail = GmailService(GmailTokenManager(account))
        stored_history_id = account.gmail_history_id

        if stored_history_id is None:
            message_ids, latest_history_id = _recent_inbox_message_ids(gmail)
        else:
            try:
                message_ids, latest_history_id = _added_message_ids_since(gmail, stored_history_id)
            except GmailServiceError as error:
                if error.status_code != 404:
                    raise
                logger.warning("Stored Gmail history id is too old; syncing recent inbox instead", extra={"account_id": str(account_id)})
                message_ids, latest_history_id = _recent_inbox_message_ids(gmail)

        new_email_ids: list[uuid.UUID] = []

        for message_id in message_ids:
            message = _get_message_or_none(gmail, message_id)

            if message is None or not SKIPPED_LABELS.isdisjoint(message.labelIds):
                continue

            email_id = create_email(
                db,
                email_account_id=account.id,
                provider_message_id=message.id,
                from_address=message.sender or "",
                subject=message.subject,
                body=message.text,
            )

            if email_id is not None:
                new_email_ids.append(email_id)

        account.gmail_history_id = _newest_history_id(stored_history_id, latest_history_id, str(notification_history_id))
        db.commit()

    return new_email_ids


def _added_message_ids_since(gmail: GmailService, start_history_id: str) -> tuple[list[str], str | None]:
    message_ids: dict[str, None] = {} 
    latest_history_id: str | None = None
    page_token: str | None = None

    while True:
        page = gmail.list_history(HistoryListRequest(
            startHistoryId=start_history_id,
            historyTypes=["messageAdded"],
            labelId=SYNC_LABEL,
            pageToken=page_token,
            maxResults=HISTORY_PAGE_SIZE,
        ))

        for record in page.history:
            for added in record.messagesAdded:
                if SKIPPED_LABELS.isdisjoint(added.message.labelIds):
                    message_ids[added.message.id] = None

        latest_history_id = page.historyId or latest_history_id
        page_token = page.nextPageToken

        if page_token is None:
            return list(message_ids), latest_history_id


def _recent_inbox_message_ids(gmail: GmailService) -> tuple[list[str], str | None]:
    baseline_history_id = gmail.get_profile().historyId
    page = gmail.get_messages(MessageListRequest(labelIds=[SYNC_LABEL], maxResults=FALLBACK_SYNC_MAX_MESSAGES))
    return [message.id for message in page.messages], baseline_history_id


def _get_message_or_none(gmail: GmailService, message_id: str) -> Message | None:
    try:
        return gmail.get_message(MessageRequest(id=message_id))
    except GmailServiceError as error:
        if error.status_code == 404:
            logger.info("Gmail message was deleted before it could be synced", extra={"gmail_message_id": message_id})
            return None
        raise


def _newest_history_id(*history_ids: str | None) -> str | None:
    numeric_ids = [int(history_id) for history_id in history_ids if history_id]
    return str(max(numeric_ids)) if numeric_ids else None
