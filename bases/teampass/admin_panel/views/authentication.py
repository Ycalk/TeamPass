from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Final, override

import structlog
from dishka.integrations.starlette import FromDishka
from opentelemetry import trace
from pydantic import BaseModel, ValidationError
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from teampass.admin_panel.settings import AdminPanelSettings
from teampass.admin_panel.utils import INJECT, inject_from_request

_logger: Final[structlog.BoundLogger] = structlog.get_logger()
_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)


class AdminType(StrEnum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"


class AdminSession(BaseModel):
    admin_type: AdminType
    expires_at: datetime


class AdminAuth(AuthenticationBackend):
    @override
    @inject_from_request
    async def login(
        self,
        request: Request,
        settings: FromDishka[AdminPanelSettings] = INJECT,
    ) -> bool:
        with _tracer.start_as_current_span("admin.login") as span:
            form = await request.form()
            username = form.get("username")
            password = form.get("password")
            if username is None or not isinstance(username, str):
                _logger.warning("no_username")
                return False
            if password is None or not isinstance(password, str):
                _logger.warning("no_password")
                return False

            span.set_attribute("admin.username", username)
            if (
                username == settings.super_admin_username
                and password == settings.super_admin_password
            ):
                admin_session = AdminSession(
                    admin_type=AdminType.SUPER_ADMIN,
                    expires_at=datetime.now(timezone.utc)
                    + timedelta(days=settings.admin_session_expire_days),
                )
                request.session.update(admin_session.model_dump(mode="json"))
                _logger.info("login_success", username=username)
                span.set_attribute("success", True)
                return True

            _logger.info("invalid_credentials", username=username)
            span.set_attribute("success", False)
            return False

    @override
    async def logout(self, request: Request) -> bool:
        with _tracer.start_as_current_span("admin.logout") as span:
            request.session.clear()
            span.set_attribute("success", True)
            return True

    @override
    async def authenticate(self, request: Request) -> bool:
        with _tracer.start_as_current_span("admin.authenticate") as span:
            try:
                admin_session = AdminSession.model_validate(request.session)
            except ValidationError as e:
                _logger.warning("invalid_session", error=e)
                span.set_attribute("success", False)
                span.record_exception(e)
                return False

            if admin_session.expires_at < datetime.now(timezone.utc):
                _logger.warning("session_expired", admin_session=admin_session)
                request.session.clear()
                span.set_attribute("success", False)
                return False

            span.set_attribute("success", True)
            return True
