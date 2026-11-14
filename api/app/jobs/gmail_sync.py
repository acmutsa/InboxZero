from app.queue.redis import redis_connection

logger = logging.getLogger(__name__)

SYNC_LOCK_TIMEOUT_SECONDS = 60

def sync_gmail_job(account_id: str, history_id: int) -> None:
    """Find the messages that arrived since the last sync of this Gmail account.

    Enqueued by the Gmail webhook as "app.jobs.gmail_sync.sync_gmail_job".
    """
    pass