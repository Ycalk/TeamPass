from typing import Annotated, Final, override

import structlog
from argon2 import PasswordHasher
from opentelemetry import trace
from pydantic import BaseModel, SecretStr, StringConstraints
from teampass.admin.dto import Admin
from teampass.admin.storage import AdminDAO
from teampass.domain_core import DomainConflictException, DomainMethod

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class AdminAlreadyExistsException(DomainConflictException):
    def __init__(self, username: str) -> None:
        self.username: str = username
        super().__init__(f"Admin with username {username} already created")


class CreateAdminCommand(BaseModel):
    username: str
    plain_password: Annotated[SecretStr, StringConstraints(min_length=8)]


class CreateAdminMethod(DomainMethod[CreateAdminCommand, Admin]):
    def __init__(
        self,
        admin_dao: AdminDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        self.admin_dao: AdminDAO = admin_dao
        self.password_hasher: PasswordHasher = password_hasher

    @override
    async def __call__(self, command: CreateAdminCommand) -> Admin:
        with _tracer.start_as_current_span("create_admin") as span:
            span.set_attribute("username", command.username)
            logger = _logger.bind(username=command.username)

            logger.info("creating_admin")

            admin = await self.admin_dao.find_by_username(command.username)
            if admin is not None:
                span.set_attribute("admin.id", str(admin.id))
                logger.error("admin_already_created")
                raise AdminAlreadyExistsException(command.username)

            password_hash = self.password_hasher.hash(
                command.plain_password.get_secret_value()
            )
            admin = await self.admin_dao.create(
                username=command.username,
                password_hash=password_hash,
            )

            span.set_attribute("admin.id", str(admin.id))
            logger.info("admin_created")
            await self.admin_dao.commit()
            return Admin.from_persistent(admin)
