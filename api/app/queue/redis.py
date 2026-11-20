import uuid

from redis import Redis
from rq import Queue
from rq import Retry
from app.config import config

JOB_TIMEOUT_SECONDS = 30
JOB_RETRY = Retry(max=2, interval=[1, 2])

redis_connection = Redis.from_url(config.REDIS_URL)
email_queue = Queue(config.REDIS_EMAIL_QUEUE, connection=redis_connection)

def get_queue() -> Queue:
    return email_queue

def enqueue_gmail(job_name:str, queue: Queue, account_id: uuid.UUID, history_id: int) -> str:
    job = queue.enqueue(job_name, str(account_id), history_id, job_timeout=JOB_TIMEOUT_SECONDS, retry=JOB_RETRY)
    return job.id
