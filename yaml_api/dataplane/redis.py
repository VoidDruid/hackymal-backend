import aioredis

from settings import redis_settings


async def get_redis():
    return await aioredis.from_url(redis_settings.uri)
