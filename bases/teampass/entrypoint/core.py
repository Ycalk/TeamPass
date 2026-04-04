import asyncio
from contextlib import asynccontextmanager

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, status
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from teampass.database import DatabaseProvider
from teampass.domain_core import DomainException
from teampass.logging import LoggingSettings, LoggingSettingsProvider, setup_logging
from teampass.user import UserProvider
from uvicorn import Config, Server

from .routers import authentication_router
from .settings import EntrypointSettings, EntrypointSettingsProvider
from .utils import (
    CustomHTTPException,
    ErrorResponse,
    all_exception_handler,
    custom_http_exception_handler,
    domain_exception_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await app.state.dishka_container.close()


async def build_app() -> FastAPI:
    container = make_async_container(
        EntrypointSettingsProvider(),
        DatabaseProvider(),
        LoggingSettingsProvider(),
        UserProvider(),
    )

    entrypoint_settings = await container.get(EntrypointSettings)
    logging_settings = await container.get(LoggingSettings)

    setup_logging(logging_settings, "api")

    app = FastAPI(
        title=entrypoint_settings.app_name,
        docs_url=entrypoint_settings.api_prefix + "/docs",
        redoc_url=entrypoint_settings.api_prefix + "/redoc",
        openapi_url=entrypoint_settings.api_prefix + "/openapi.json",
        swagger_ui_oauth2_redirect_url=entrypoint_settings.api_prefix
        + "/docs/oauth2-redirect",
        lifespan=lifespan,
        responses={
            status.HTTP_500_INTERNAL_SERVER_ERROR: {
                "model": ErrorResponse,
                "description": "Внутренняя ошибка сервера",
            },
        },
    )

    FastAPIInstrumentor.instrument_app(app)

    setup_dishka(container=container, app=app)

    app.add_exception_handler(CustomHTTPException, custom_http_exception_handler)
    app.add_exception_handler(DomainException, domain_exception_handler)
    app.add_exception_handler(Exception, all_exception_handler)

    app.include_router(authentication_router, prefix=entrypoint_settings.api_prefix)

    return app


async def run_app() -> None:
    app = await build_app()
    entrypoint_settings: EntrypointSettings = await app.state.dishka_container.get(
        EntrypointSettings
    )

    config = Config(
        app=app,
        host="0.0.0.0",
        port=entrypoint_settings.api_port,
        reload=False,
    )
    server = Server(config)
    await server.serve()


def run() -> None:
    asyncio.run(run_app())
