import uuid

from redis import Redis
from rq import Queue
from rq import Retry
from app.config import config

JOB_TIMEOUT_SECONDS = 30
JOB_RETRY = Retry(max=2, interval=[1, 2])

PROCESS_EMAIL_JOB = "app.jobs.process_email.process_email"
# Room for the classifier, the drafter, and up to two draft retries.
PROCESS_EMAIL_TIMEOUT_SECONDS = 300

redis_connection = Redis.from_url(config.REDIS_URL)
email_queue = Queue(config.REDIS_EMAIL_QUEUE, connection=redis_connection)

def get_queue() -> Queue:
    return email_queue

def enqueue_gmail(job_name:str, queue: Queue, account_id: uuid.UUID, history_id: int) -> str:
    job = queue.enqueue(job_name, str(account_id), history_id, job_timeout=JOB_TIMEOUT_SECONDS, retry=JOB_RETRY)
    return job.id

def enqueue_outlook(job_name: str, queue: Queue, account_id: uuid.UUID, message_id: str) -> str:
    job = queue.enqueue(job_name, str(account_id), message_id, job_timeout=JOB_TIMEOUT_SECONDS, retry=JOB_RETRY)
    
def enqueue_process_email(queue: Queue, email_id: uuid.UUID) -> str:
    # A fixed job id per email keeps one email from being queued twice at once.
    job = queue.enqueue(PROCESS_EMAIL_JOB, str(email_id), job_id=f"process-email-{email_id}", job_timeout=PROCESS_EMAIL_TIMEOUT_SECONDS)
    return job.id
