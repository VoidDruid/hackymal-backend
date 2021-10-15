# pylint: disable=C0413

from typing import Any

from service.api import Api


api: Api = Api(tags=["ВРЕМЕННО"])


@api.post("/tests", response_model=Any)
async def variant_1() -> Any:
    pass
