from uuid import uuid4

import aioredis

from .consts import SESSION_TTL


def create_session_id() -> str:
    return uuid4().hex


async def create_session(redis: aioredis.Redis) -> str:
    session_id = create_session_id()

    await redis.hset(session_id, "online", 1)
    await redis.expire(session_id, SESSION_TTL)

    return session_id
