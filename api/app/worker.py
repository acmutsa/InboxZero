import sys

from rq import Queue
from rq import Worker

from app.queue.redis import draft_queue
from app.queue.redis import redis_connection
from app.queue.redis import sync_queue

WORKERS: dict[str, Queue] = {
    "sync": sync_queue,
    "draft": draft_queue,
}

def main(argv: list[str]) -> None:
    if len(argv) != 1 or argv[0] not in WORKERS:
        sys.exit(f"usage: python -m app.worker {{{'|'.join(WORKERS)}}}")

    Worker([WORKERS[argv[0]]], connection=redis_connection).work(with_scheduler=True)


if __name__ == "__main__":
    main(sys.argv[1:])
