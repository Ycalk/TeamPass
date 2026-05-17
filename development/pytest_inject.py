import inspect
from collections.abc import Callable
from functools import wraps
from typing import Annotated, Any, get_args, get_origin

from dishka import AsyncContainer


def inject(func: Callable[..., Any]):
    sig = inspect.signature(func)
    injectable_params = {}
    for name, param in sig.parameters.items():
        if get_origin(param.annotation) is Annotated:
            args = get_args(param.annotation)
            base_type = args[0]
            metadata = args[1:]
            if any(type(meta).__name__ == "_FromComponent" for meta in metadata):
                injectable_params[name] = base_type

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any):
        container: AsyncContainer = kwargs.pop("request_container")
        for name, dep_type in injectable_params.items():
            if name not in kwargs:
                kwargs[name] = await container.get(dep_type)
        kwargs.pop("request_container", None)
        return await func(*args, **kwargs)

    new_params: list[inspect.Parameter] = []
    needs_container = True

    for name, param in sig.parameters.items():
        if name in injectable_params:
            continue
        if name == "request_container":
            needs_container = False
        new_params.append(param)

    if needs_container:
        new_params.append(
            inspect.Parameter(
                name="request_container",
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=AsyncContainer,
            )
        )

    setattr(wrapper, "__signature__", sig.replace(parameters=new_params))
    return wrapper
