from urllib.parse import urlparse

from arq.connections import RedisSettings

from app.config import config


def get_redis_settings() -> RedisSettings:
    redis_url = config.REDIS_URL
    url = urlparse(redis_url)

    return RedisSettings(
        host=url.hostname or "localhost",
        port=url.port or 6379,
        database=int(url.path.lstrip("/") or 0),
        username=url.username,
        password=url.password,
        ssl=url.scheme == "rediss",
    )