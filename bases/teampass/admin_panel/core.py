import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.starlette import StarletteProvider, setup_dishka
from opentelemetry.instrumentation.starlette import StarletteInstrumentor
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware
from teampass.admin import AdminProvider
from teampass.database import DatabaseProvider
from teampass.logging import LoggingSettings, LoggingSettingsProvider, setup_logging
from teampass.team import TeamProvider
from teampass.user import UserProvider
from uvicorn import Config, Server

from .settings import AdminPanelSettings
from .views import AdminAuth, AdminView, ChangePasswordView


class AdminPanelProvider(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> AdminPanelSettings:
        return AdminPanelSettings()  # type: ignore # pyright: ignore


@asynccontextmanager
async def lifespan(app: Starlette):
    yield
    await app.state.dishka_container.close()


async def build_app() -> Starlette:
    container = make_async_container(
        AdminPanelProvider(),
        AdminProvider(),
        StarletteProvider(),
        DatabaseProvider(),
        LoggingSettingsProvider(),
        UserProvider(),
        TeamProvider(),
    )

    admin_panel_settings = await container.get(AdminPanelSettings)
    logging_settings = await container.get(LoggingSettings)

    setup_logging(logging_settings, "admin_panel")

    app = Starlette(
        lifespan=lifespan,
    )
    app.add_middleware(SessionMiddleware, secret_key=admin_panel_settings.secret_key)
    StarletteInstrumentor.instrument_app(app)
    setup_dishka(container=container, app=app)

    current_dir = Path(__file__).resolve().parent
    templates_dir = current_dir / "templates"
    if not templates_dir.exists():
        raise RuntimeError(f"Templates directory not found: {templates_dir}")
    authentication_backend = AdminAuth(secret_key=admin_panel_settings.secret_key)
    admin = Admin(
        app,
        await container.get(AsyncEngine),
        base_url="",
        title=admin_panel_settings.app_name,
        templates_dir=str(templates_dir),
        authentication_backend=authentication_backend,
    )
    admin.add_view(AdminView)
    admin.add_view(ChangePasswordView)

    return app


async def run_app() -> None:
    app = await build_app()
    admin_panel_settings: AdminPanelSettings = await app.state.dishka_container.get(
        AdminPanelSettings
    )

    config = Config(
        app=app,
        host="0.0.0.0",
        port=admin_panel_settings.app_port,
        reload=False,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
    server = Server(config)
    await server.serve()


def run() -> None:
    asyncio.run(run_app())
