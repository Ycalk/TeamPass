from typing import Final, override

import structlog
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from opentelemetry import trace
from pydantic import BaseModel, SecretStr
from teampass.admin.dto import Admin
from teampass.admin.storage import AdminDAO
from teampass.domain_core import DomainMethod, DomainUnauthorizedException

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class InvalidUsernameOrPasswordException(DomainUnauthorizedException):
    def __init__(self, username: str) -> None:
        self.username: str = username
        super().__init__(f"Invalid username or password for username {username}")


class LoginAdminCommand(BaseModel):
    username: str
    plain_password: SecretStr


class LoginAdminMethod(DomainMethod[LoginAdminCommand, Admin]):
    def __init__(
        self,
        admin_dao: AdminDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        self.admin_dao: AdminDAO = admin_dao
        self.password_hasher: PasswordHasher = password_hasher

    @override
    async def __call__(self, command: LoginAdminCommand) -> Admin:
        with _tracer.start_as_current_span("login_admin") as span:
            span.set_attribute("username", command.username)
            logger = _logger.bind(username=command.username)

            logger.info("login_admin")

            admin = await self.admin_dao.find_by_username(command.username)
            if admin is None:
                raise InvalidUsernameOrPasswordException(command.username)

            span.set_attribute("admin.id", str(admin.id))
            logger.info("admin_found")

            try:
                self.password_hasher.verify(
                    admin.password_hash, command.plain_password.get_secret_value()
                )
            except VerifyMismatchError as e:
                logger.error("invalid_password")
                raise InvalidUsernameOrPasswordException(command.username) from e
            logger.info("password_verified")

            return Admin.from_persistent(admin)
