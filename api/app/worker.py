from rq import Worker

from app.config import config
from app.queue.redis import redis_connection

if __name__ == "__main__":
    # Listen on the same queue the API enqueues to. The scheduler is needed for
    # retries with an interval (JOB_RETRY); without it they never run.
    Worker([config.REDIS_EMAIL_QUEUE], connection=redis_connection).work(with_scheduler=True)
