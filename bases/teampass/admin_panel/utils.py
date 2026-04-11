import inspect
from collections.abc import Callable
from datetime import datetime
from enum import StrEnum
from functools import wraps
from typing import Annotated, Any, Self, cast, get_args, get_origin
from uuid import UUID

from dishka import AsyncContainer
from pydantic import BaseModel, model_validator
from starlette.requests import Request

INJECT: Any = object()


def inject_from_request[F: Callable[..., Any]](func: F) -> F:
    sig = inspect.signature(func)

    dependencies_to_inject: dict[str, Any] = {}
    for name, param in sig.parameters.items():
        if param.default is INJECT:
            annotation = param.annotation
            if get_origin(annotation) is Annotated:
                dependency_type = get_args(annotation)[0]
            else:
                dependency_type = annotation
            dependencies_to_inject[name] = dependency_type

    if not dependencies_to_inject:
        return func

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        request = bound_args.arguments.get("request")
        if not isinstance(request, Request):
            raise TypeError("request must be a Request")

        container: AsyncContainer = request.state.dishka_container

        async with container() as request_container:
            for name, dependency_type in dependencies_to_inject.items():
                bound_args.arguments[name] = await request_container.get(
                    dependency_type
                )

        return await func(*bound_args.args, **bound_args.kwargs)

    return cast(F, wrapper)


class AdminType(StrEnum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"


class AdminSession(BaseModel):
    id: UUID | None
    password_hash: str | None
    admin_type: AdminType
    expires_at: datetime

    @model_validator(mode="after")
    def validate_id_for_admin_type(self) -> Self:
        if self.admin_type == AdminType.SUPER_ADMIN and (
            self.id is not None or self.password_hash is None
        ):
            raise ValueError(
                "id must be None and password_hash must not be None for super admin"
            )
        if self.admin_type != AdminType.SUPER_ADMIN and (
            self.id is None or self.password_hash is not None
        ):
            raise ValueError(
                "id must not be None and password_hash must be None for regular admin"
            )
        return self
