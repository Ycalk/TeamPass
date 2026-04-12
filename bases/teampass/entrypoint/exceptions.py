from typing import Self

from fastapi import Request, status
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from teampass.domain_core import (
    DomainConflictException,
    DomainException,
    DomainForbiddenException,
    DomainNotFoundException,
    DomainUnauthorizedException,
)

from .scheme import ErrorResponse


class CustomHTTPException(Exception):
    def __init__(
        self,
        error: str,
        message: str,
        status_code: int,
        headers: dict[str, str] | None = None,
    ):
        self.status_code: int = status_code
        self.error: str = error
        self.message: str = message
        self.headers: dict[str, str] | None = headers

        super().__init__(message)

    @classmethod
    def from_exception(
        cls,
        exc: Exception,
        status_code: int,
        message: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> Self:
        return cls(
            status_code=status_code,
            error=exc.__class__.__name__,
            message=message if message else str(exc),
            headers=headers,
        )


def custom_http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, CustomHTTPException):
        error_response = ErrorResponse(
            error="UnexpectedMappingError",
            message="Unexpected exception mapping. Expect CustomHTTPException, "
            + f"got {exc.__class__.__name__}",
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(),
        )

    error_response = ErrorResponse(error=exc.error, message=exc.message)
    span = trace.get_current_span()
    span.record_exception(exc)
    span.set_attribute("error", exc.error)
    span.set_attribute("message", exc.message)
    span.set_attribute("status_code", exc.status_code)
    span.set_attribute("request.path", request.url.path)
    span.set_attribute("request.method", request.method)
    span.set_status(status=Status(StatusCode.ERROR, exc.error))

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
        headers=exc.headers,
    )


def all_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    error_response = ErrorResponse(error=exc.__class__.__name__, message=str(exc))
    span = trace.get_current_span()
    span.record_exception(exc)
    span.set_attribute("error", error_response.error)
    span.set_attribute("message", error_response.message)
    span.set_attribute("status_code", status.HTTP_500_INTERNAL_SERVER_ERROR)
    span.set_attribute("request.path", request.url.path)
    span.set_attribute("request.method", request.method)
    span.set_status(status=Status(StatusCode.ERROR, error_response.message))

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(),
    )


def domain_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, DomainException):
        error_response = ErrorResponse(
            error="UnexpectedMappingError",
            message="Unexpected exception mapping. Expect DomainException, "
            + f"got {exc.__class__.__name__}",
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(),
        )

    if isinstance(exc, DomainUnauthorizedException):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, DomainForbiddenException):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, DomainConflictException):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, DomainNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    else:
        status_code = status.HTTP_400_BAD_REQUEST

    error_response = ErrorResponse(error=exc.__class__.__name__, message=str(exc))
    span = trace.get_current_span()
    span.record_exception(exc)
    span.set_attribute("error", error_response.error)
    span.set_attribute("message", error_response.message)
    span.set_attribute("status_code", status_code)
    span.set_attribute("request.path", request.url.path)
    span.set_attribute("request.method", request.method)
    span.set_status(status=Status(StatusCode.ERROR, error_response.message))

    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump(),
    )
