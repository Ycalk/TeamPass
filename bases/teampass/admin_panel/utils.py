import inspect
from collections.abc import Callable
from functools import wraps
from typing import Annotated, Any, cast, get_args, get_origin

from dishka import AsyncContainer
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
