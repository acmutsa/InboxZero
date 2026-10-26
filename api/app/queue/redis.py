import os
from urllib.parse import urlparse

from arq.connections import RedisSettings


def get_redis_settings() -> RedisSettings:
    redis_url = os.getenv("REDIS_URL")

    if not redis_url:
        raise RuntimeError("REDIS_URL environment variable is not configured")

    url = urlparse(redis_url)

    return RedisSettings(
        host=url.hostname or "localhost",
        port=url.port or 6379,
        database=int(url.path.lstrip("/") or 0),
        username=url.username,
        password=url.password,
        ssl=url.scheme == "rediss",
    )