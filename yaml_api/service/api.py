# pylint: disable=R0915,W0612,C0415,R1702  ; complexity warnings

from typing import Any, Callable, Dict, List, Optional, Union

from fastapi import APIRouter, FastAPI
from fastapi.datastructures import DefaultPlaceholder
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import UJSONResponse
from loguru import logger
from starlette.requests import Request

import settings
from domain.exceptions import DomainError

from .schemas import ErrorResponse


class FormedResponse(UJSONResponse):
    def render(self, content: Any) -> bytes:
        return super().render({"items": content})


def make_app(*args: Any, **kwargs: Any) -> FastAPI:
    kwargs.setdefault("docs_url", "/api")
    kwargs.setdefault("debug", settings.DEBUG)
    kwargs.setdefault("title", settings.APP_NAME),
    kwargs.setdefault("version", settings.APP_VERSION),
    kwargs.setdefault("openapi_url", "/api/openapi.json")

    app = FastAPI(*args, **kwargs)

    set_middlewares(app)

    # it is covered (I think??), cov just does not see it for some reason
    if settings.DEBUG:  # pragma: no cover
        from starlette.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["*"],
        )

    return app


def set_middlewares(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    def type_error_handler(
        request: Request, exc: RequestValidationError
    ) -> FormedResponse:
        return FormedResponse(
            status_code=422,
            content={"ok": False, "error": exc.errors()},
        )

    @app.exception_handler(DomainError)
    def domain_error_handler(request: Request, exc: DomainError) -> FormedResponse:
        return FormedResponse(
            status_code=400,
            content={"ok": False, "error": exc.msg},
        )

    @app.exception_handler(Error)
    def error_handler(request: Request, exc: Error) -> FormedResponse:
        return exc.render()

    @app.exception_handler(HTTPException)
    def fastapi_error_handler(request: Request, exc: HTTPException) -> FormedResponse:
        return FormedResponse(
            status_code=exc.status_code,
            content={"ok": False, "error": exc.detail},
            headers=exc.headers or {},
        )

    @app.middleware("http")
    async def catch_exceptions_middleware(
        request: Request, call_next: Callable[[Request], Any]
    ) -> FormedResponse:
        try:
            return await call_next(request)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Uncaught exception while processsing request")
            return InternalError(str(exc)).render()


class Api(APIRouter):
    def api_route(
        self, *args: Any, **kwargs: Any
    ) -> Callable[..., Any]:  # pylint: disable=W0221
        if type(kwargs["response_class"]) == DefaultPlaceholder:
            kwargs["response_class"] = FormedResponse
        return super().api_route(*args, **kwargs)


class ResponsesContainer(dict):
    default_responses = {
        400: {"model": ErrorResponse, "description": "General error"},
    }
    errors_dict = {}

    def __init__(self) -> None:
        dict.__init__(self, self.default_responses)

    def __call__(
        self, extra: Optional[Union[str, List[str]]] = None
    ) -> Dict[int, Dict]:
        result_responses = self.default_responses.copy()
        if extra:
            if isinstance(extra, str):
                extra = [extra]
            for key in extra:
                if key not in self.errors_dict:
                    raise ValueError(f"Invalid error key {key}")
                response = self.errors_dict[key]
                result_responses[response[0]] = response[1]
        return result_responses


responses = ResponsesContainer()


class Error(HTTPException):
    error: Optional[Union[str, Dict, List]] = None
    status_code: int = 400
    error_code: str = "Error"
    description = "Oh no!"
    headers: Optional[Dict[str, str]] = None

    def __init_subclass__(cls) -> None:
        error_response = (
            cls.status_code,
            {"model": ErrorResponse, "description": cls.description},
        )
        ResponsesContainer.errors_dict.update(
            {
                cls.status_code: error_response,
                cls.error_code.lower(): error_response,
            }
        )
        return super().__init_subclass__()

    def __init__(self, *args: Any, **kwargs: Any):
        if self.error is None:
            if len(args) == 1:
                self.error = args[0]
            else:
                raise ValueError("Only one positional arg is accepted - error message")

            self.status_code = kwargs.get("status_code", self.status_code)
            self.error_code = kwargs.get("error_code", self.error_code)

            if self.error is None:
                raise ValueError(
                    "Provide only error message or set default error template in error class to use arguments"
                )
        else:
            self.error = self.error.format(*args, **kwargs)  # type: ignore
        super().__init__(
            status_code=self.status_code, detail=self.error, headers=self.headers
        )

    def render(self) -> FormedResponse:
        return FormedResponse(
            status_code=self.status_code,
            content=ErrorResponse(error=self.error, error_code=self.error_code).dict(),
            headers=self.headers or {},
        )


class UnauthorizedError(Error):
    status_code = 401
    error_code = "UNAUTHORIZED"
    description = "User is not authorized"


class PermissionsError(Error):
    status_code = 403
    error_code = "INVALID_PERMISSIONS"
    description = "User does not have permissions to perform this action"


class NotFoundError(Error):
    status_code = 404
    error_code = "NOT_FOUND"
    description = "Requested resource was not found"


class InternalError(Error):
    status_code = 500
    error_code = "INTERNAL_SERVER_ERROR"


class InvalidRequestError(Error):
    status_code = 400
    error_code = "INVALID_REQUEST"
