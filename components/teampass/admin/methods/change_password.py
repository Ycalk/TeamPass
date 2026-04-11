from typing import Final, override
from uuid import UUID

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
    def __init__(self, admin_id: UUID) -> None:
        self.admin_id: UUID = admin_id
        super().__init__(f"Admin with id {admin_id} not found")


class InvalidPasswordException(DomainUnauthorizedException):
    def __init__(self, admin_id: UUID) -> None:
        self.admin_id: UUID = admin_id
        super().__init__(f"Invalid password for admin with id {admin_id}")


class ChangeAdminPasswordCommand(BaseModel):
    admin_id: UUID
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
            logger = _logger.bind(admin_id=str(command.admin_id))
            logger.info("change_admin_password")

            admin = await self.admin_dao.find_by_id(command.admin_id)
            if admin is None:
                raise AdminNotFoundException(command.admin_id)

            span.set_attribute("admin.id", str(admin.id))
            logger.info("admin_found")

            try:
                self.password_hasher.verify(
                    admin.password_hash, command.current_password.get_secret_value()
                )
            except VerifyMismatchError as e:
                logger.error("invalid_password")
                raise InvalidPasswordException(command.admin_id) from e
            logger.info("password_verified")

            admin.password_hash = self.password_hasher.hash(
                command.new_password.get_secret_value()
            )
            await self.admin_dao.save(admin)
            logger.info("password_changed")
            await self.admin_dao.commit()

            return Admin.from_persistent(admin)
