import json
from datetime import datetime, timezone

from app.queue.redis import get_redis_settings
from arq import Retry

async def test_job(ctx, name: str):
    print(f"Processing job for: {name}")

    return {
        "status": "completed",
        "name": name
    }

async def retry_test_job(ctx, name: str):
    job_try = ctx["job_try"]

    print(f"Attempt {job_try} for: {name}")

    if job_try < 3:
        delay = 2 ** (job_try - 1)
        print(f"Job failed. Retrying in {delay} seconds...")
        raise Retry(defer=delay)

    print(f"Successfully processed: {name}")\

    return {
        "status": "completed",
        "name": name,
        "attempts": job_try
    }

async def dead_letter_test_job(ctx, name: str):
    job_try = ctx["job_try"]

    print(f"Dead-letter test: attempt {job_try} for {name}")

    error = "Simulated permanent processing failure"

    if job_try < 3:
        delay = 2 ** (job_try - 1)
        print(f"Job failed. Retrying in {delay} seconds...")
        raise Retry(defer=delay)

    dead_letter = {
        "job_id": ctx["job_id"],
        "job_name": "dead_letter_test_job",
        "name": name,
        "attempts": job_try,
        "error": error,
        "failed_at": datetime.now(timezone.utc).isoformat()
    }

    await ctx["redis"].lpush(
        "inboxzero:dead_letters",
        json.dumps(dead_letter)
    )

    print(f"Job moved to dead-letter handling: {ctx['job_id']}")

    raise RuntimeError(error)

class WorkerSettings:
    functions = [
        test_job,
        retry_test_job,
        dead_letter_test_job
    ]
    
    redis_settings = get_redis_settings()
    max_tries = 3