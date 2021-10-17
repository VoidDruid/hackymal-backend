# pylint: disable=C0413

from typing import Any

import aioredis
import networkx as nx
from fastapi import Depends

from dataplane import get_redis
from domain.routing import calculate_paths, get_graph
from service.api import Api


api: Api = Api(tags=["ВРЕМЕННО"])


@api.post("/tests", response_model=Any)
async def tests(redis: aioredis.Redis = Depends(get_redis)) -> Any:
    return await calculate_paths(redis)
