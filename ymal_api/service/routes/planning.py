# pylint: disable=C0413

from typing import Any

import aioredis
from fastapi import Depends

from dataplane import get_redis
from domain.routing import calculate_paths
from service.api import Api


api: Api = Api(tags=["Планировщик"])


@api.post("/", response_model=Any)
async def plan(redis: aioredis.Redis = Depends(get_redis)) -> Any:
    # FIXME!!!
    n = 0
    while n < 7:
        try:
            return await calculate_paths(redis)
        except:
            n += 1
    raise RuntimeError("We are fucked")
