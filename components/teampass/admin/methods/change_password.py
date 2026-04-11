from typing import Final, override

import structlog
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from opentelemetry import trace
from pydantic import BaseModel, SecretStr
from teampass.admin.dto import Admin
from teampass.admin.storage import AdminDAO
from teampass.domain_core import (
    DomainMethod,
    DomainNotFoundException,
    DomainUnauthorizedException,
)

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class AdminNotFoundException(DomainNotFoundException):
    def __init__(self, username: str) -> None:
        self.username: str = username
        super().__init__(f"Username {username} not found")


class InvalidPasswordException(DomainUnauthorizedException):
    def __init__(self, username: str) -> None:
        self.username: str = username
        super().__init__(f"Invalid password for username {username}")


class ChangeAdminPasswordCommand(BaseModel):
    username: str
    current_password: SecretStr
    new_password: SecretStr


class ChangeAdminPasswordMethod(DomainMethod[ChangeAdminPasswordCommand, Admin]):
    def __init__(
        self,
        admin_dao: AdminDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        self.admin_dao: AdminDAO = admin_dao
        self.password_hasher: PasswordHasher = password_hasher

    @override
    async def __call__(self, command: ChangeAdminPasswordCommand) -> Admin:
        with _tracer.start_as_current_span("change_admin_password") as span:
            span.set_attribute("username", command.username)
            logger = _logger.bind(username=command.username)
            logger.info("change_admin_password")

            admin = await self.admin_dao.find_by_username(command.username)
            if admin is None:
                raise AdminNotFoundException(command.username)

            span.set_attribute("admin.id", str(admin.id))
            logger.info("admin_found")

            try:
                self.password_hasher.verify(
                    admin.password_hash, command.current_password.get_secret_value()
                )
            except VerifyMismatchError as e:
                logger.error("invalid_password")
                raise InvalidPasswordException(command.username) from e
            logger.info("password_verified")

            admin.password_hash = self.password_hasher.hash(
                command.new_password.get_secret_value()
            )
            await self.admin_dao.save(admin)
            logger.info("password_changed")
            await self.admin_dao.commit()

            return Admin.from_persistent(admin)
