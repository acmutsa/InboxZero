import asyncio
import json
import logging
from datetime import datetime, timezone

from app.queue.redis import get_redis_settings
from arq import Retry
from app.workflows.email_processing import process_email

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3
RETRY_DELAYS = [1, 2]
EMAIL_PROCESSING_TIMEOUT = 30

async def process_email_job(ctx, account_id: str, message_id: str):

    try:
        async with asyncio.timeout(EMAIL_PROCESSING_TIMEOUT):
            result = await process_email(account_id, message_id)

        return {
            "status": "completed",
            "account_id": account_id,
            "message_id": message_id,
            "result": result
        }

    except Exception as e:
        job_try = ctx["job_try"]

        if job_try < MAX_ATTEMPTS:
            delay = RETRY_DELAYS[job_try - 1]
            logger.warning(f"Email processing failed. Retrying in {delay} seconds...")
            raise Retry(defer=delay)

        dead_letter = {
            "job_id": ctx["job_id"],
            "job_name": "process_email_job",
            "account_id": account_id,
            "message_id": message_id,
            "attempts": job_try,
            "error": str(e),
            "failed_at": datetime.now(timezone.utc).isoformat()
        }

        await ctx["redis"].lpush(
            "inboxzero:dead_letters",
            json.dumps(dead_letter)
        )

        logger.error(f"Email moved to dead-letter list: {ctx['job_id']}")

        raise

class WorkerSettings:
    functions = [process_email_job]
    
    redis_settings = get_redis_settings()
    max_tries = MAX_ATTEMPTS