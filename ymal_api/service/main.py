from typing import Dict

from common.logger import init_logger
from settings import settings

from .api import Api, make_app
from .routes import temp_api


app = make_app()

if not settings.DEBUG:
    # Init logger in JSON format
    init_logger(
        settings.LOG_LEVEL,
        settings.LOG_FORMAT,
        keep_loggers=["uvicorn.access"],
        suppress_loggers=["uvicorn", "uvicorn.error", "fastapi"],
    )

api_v1 = Api()
api_v1.include_router(temp_api, prefix="/temp")


@app.get("/healthz", tags=["health check"])
async def root() -> Dict[str, bool]:
    """Health check endpoint"""
    return {"ok": True}


app.include_router(api_v1, prefix="/api/v1")
