from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Final, Self, override
from uuid import UUID

import structlog
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from dishka.integrations.starlette import FromDishka
from opentelemetry import trace
from pydantic import BaseModel, SecretStr, ValidationError, model_validator
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from teampass.admin import (
    InvalidUsernameOrPasswordException,
    LoginAdminCommand,
    LoginAdminMethod,
)
from teampass.admin.storage import AdminDAO
from teampass.admin_panel.inject import (
    INJECT,
    inject_from_request,
)
from teampass.admin_panel.settings import AdminPanelSettings

_logger: Final[structlog.BoundLogger] = structlog.get_logger()
_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)


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


class AdminAuth(AuthenticationBackend):
    @override
    @inject_from_request
    async def login(
        self,
        request: Request,
        settings: FromDishka[AdminPanelSettings] = INJECT,
        login_admin_method: FromDishka[LoginAdminMethod] = INJECT,
        password_hasher: FromDishka[PasswordHasher] = INJECT,
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
                span.set_attribute("admin.type", "super_admin")
                admin_session = AdminSession(
                    id=None,
                    admin_type=AdminType.SUPER_ADMIN,
                    expires_at=datetime.now(timezone.utc)
                    + timedelta(days=settings.admin_session_expire_days),
                    password_hash=password_hasher.hash(password),
                )
                request.session.update(admin_session.model_dump(mode="json"))
                _logger.info("login_success", username=username)
                return True

            span.set_attribute("admin.type", "admin")
            try:
                admin = await login_admin_method(
                    LoginAdminCommand(
                        username=username,
                        plain_password=SecretStr(password),
                    )
                )
            except InvalidUsernameOrPasswordException:
                _logger.error("invalid_username_or_password")
                return False

            span.set_attribute("admin.id", str(admin.id))
            admin_session = AdminSession(
                id=admin.id,
                admin_type=AdminType.ADMIN,
                expires_at=datetime.now(timezone.utc)
                + timedelta(days=settings.admin_session_expire_days),
                password_hash=None,
            )
            request.session.update(admin_session.model_dump(mode="json"))
            _logger.info("login_success", username=username)
            return True

    @override
    async def logout(self, request: Request) -> bool:
        with _tracer.start_as_current_span("admin.logout") as span:
            request.session.clear()
            span.set_attribute("success", True)
            return True

    @override
    @inject_from_request
    async def authenticate(
        self,
        request: Request,
        admin_dao: FromDishka[AdminDAO] = INJECT,
        password_hasher: FromDishka[PasswordHasher] = INJECT,
        settings: FromDishka[AdminPanelSettings] = INJECT,
    ) -> bool:
        with _tracer.start_as_current_span("admin.authenticate") as span:
            try:
                admin_session = AdminSession.model_validate(request.session)
            except ValidationError as e:
                _logger.warning("invalid_session", error=e)
                span.set_attribute("success", False)
                span.record_exception(e)
                return False

            span.set_attribute("admin.id", str(admin_session.id or "none"))
            span.set_attribute("admin.type", admin_session.admin_type.value)
            span.set_attribute("admin.expires_at", admin_session.expires_at.isoformat())

            if admin_session.expires_at < datetime.now(timezone.utc):
                _logger.warning("session_expired", admin_session=admin_session)
                request.session.clear()
                span.set_attribute("success", False)
                return False

            if admin_session.id is None:
                if admin_session.password_hash is None:
                    _logger.warning("no_password_hash", admin_session=admin_session)
                    request.session.clear()
                    span.set_attribute("success", False)
                    return False

                try:
                    password_hasher.verify(
                        admin_session.password_hash,
                        settings.super_admin_password,
                    )
                    span.set_attribute("success", True)
                    return True
                except (VerifyMismatchError, InvalidHashError):
                    _logger.error("invalid_password")
                    request.session.clear()
                    span.set_attribute("success", False)
                    return False

            if not await admin_dao.exists_by_id(admin_session.id):
                _logger.warning("admin_not_found", admin_session=admin_session)
                request.session.clear()
                span.set_attribute("success", False)
                return False

            span.set_attribute("success", True)
            return True
