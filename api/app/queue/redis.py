import uuid

from redis import Redis
from rq import Queue
from rq import Retry
from app.config import config

JOB_TIMEOUT_SECONDS = 30
JOB_RETRY = Retry(max=2, interval=[1, 2])

DRAFT_EMAIL_JOB = "app.jobs.process_email.process_email"
DRAFT_EMAIL_TIMEOUT_SECONDS = 300

redis_connection = Redis.from_url(config.REDIS_URL)

sync_queue = Queue(config.REDIS_SYNC_QUEUE, connection=redis_connection)
draft_queue = Queue(config.REDIS_DRAFT_QUEUE, connection=redis_connection)

def get_sync_queue() -> Queue:
    return sync_queue

def enqueue_new_gmail(job_name:str, queue: Queue, account_id: uuid.UUID, history_id: int) -> str:
    job = queue.enqueue(job_name, str(account_id), history_id, job_timeout=JOB_TIMEOUT_SECONDS, retry=JOB_RETRY)
    return job.id

def enqueue_new_outlook(job_name: str, queue: Queue, account_id: uuid.UUID, message_id: str) -> str:
    job = queue.enqueue(job_name, str(account_id), message_id, job_timeout=JOB_TIMEOUT_SECONDS, retry=JOB_RETRY)
    return job.id

def enqueue_draft_email(queue: Queue, email_id: uuid.UUID) -> str:
    job = queue.enqueue(DRAFT_EMAIL_JOB, str(email_id), job_id=f"draft-email-{email_id}", job_timeout=DRAFT_EMAIL_TIMEOUT_SECONDS)
    return job.id
