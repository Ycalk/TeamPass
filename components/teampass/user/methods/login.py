from typing import Final, override

import structlog
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from opentelemetry import trace
from pydantic import BaseModel, EmailStr, SecretStr
from teampass.domain_core import DomainMethod
from teampass.user.dto import User
from teampass.user.storage import UserDAO

from .exceptions import InvalidEmailOrPasswordException

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class LoginUserCommand(BaseModel):
    email: EmailStr
    plain_password: SecretStr


class LoginUserMethod(DomainMethod[LoginUserCommand, User]):
    def __init__(
        self,
        user_dao: UserDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        self.user_dao: UserDAO = user_dao
        self.password_hasher: PasswordHasher = password_hasher

    @override
    async def __call__(self, command: LoginUserCommand) -> User:
        with _tracer.start_as_current_span("user.login") as span:
            span.set_attribute("user.email", command.email)
            logger = _logger.bind(email=command.email)

            logger.info("login_user")

            user = await self.user_dao.find_by_email(command.email)
            if user is None:
                raise InvalidEmailOrPasswordException(command.email)

            span.set_attribute("user.id", str(user.id))
            logger.info("user_found")

            try:
                self.password_hasher.verify(
                    user.password_hash, command.plain_password.get_secret_value()
                )
            except VerifyMismatchError as e:
                logger.error("invalid_password")
                raise InvalidEmailOrPasswordException(command.email) from e
            logger.info("password_verified")

            await user.awaitable_attrs.student
            return User.from_persistent(user)
