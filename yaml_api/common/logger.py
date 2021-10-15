from __future__ import annotations

import json
import logging
from typing import List, Optional

import loguru
from loguru import logger


class InterceptHandler(logging.Handler):  # pragma: no cover
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = record.levelno  # type: ignore[assignment]

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            if frame.f_back is None:
                break
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def sink_serializer(
    message: loguru.Message,  # pylint: disable=no-member
) -> None:  # pragma: no cover
    record = message.record
    simplified = {
        "level": record["level"].name,
        "timestamp": record["time"].timestamp(),
        "name": record["name"],
        "function": record["function"],
        "line": record["line"],
        "message": record["message"],
        "extra": record["extra"],
    }
    print(json.dumps(simplified, default=str))  # noqa: T001


def init_logger(
    level: str,
    fmt: str,
    keep_loggers: Optional[List[str]] = None,
    suppress_loggers: Optional[List[str]] = None,
) -> None:  # pragma: no cover
    """Создание loguru логгера"""

    logger.remove()
    logger.add(
        sink_serializer,
        backtrace=True,
        colorize=False,
        format=fmt,
        enqueue=True,
        level=level.upper(),
    )

    keep_loggers = keep_loggers or []
    suppress_loggers = suppress_loggers or []

    for _log in keep_loggers:
        logging.getLogger(_log).handlers = [InterceptHandler()]

    for _log in suppress_loggers:
        _logger = logging.getLogger(_log)
        _logger.propagate = False
        _logger.handlers = [InterceptHandler()]
