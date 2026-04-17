from typing import Annotated, Final, override
from uuid import UUID

import structlog
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from opentelemetry import trace
from pydantic import BaseModel, SecretStr, StringConstraints
from teampass.domain_core import DomainMethod
from teampass.user.dto import User
from teampass.user.storage import UserDAO, UserLoadEnum

from .exceptions import InvalidPasswordException, UserNotFoundException

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class ChangeUserPasswordPayload(BaseModel):
    current_password: SecretStr
    new_password: Annotated[SecretStr, StringConstraints(min_length=8)]


class ChangeUserPasswordCommand(ChangeUserPasswordPayload):
    user_id: UUID


class ChangeUserPasswordMethod(DomainMethod[ChangeUserPasswordCommand, User]):
    def __init__(
        self,
        user_dao: UserDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        self.user_dao: UserDAO = user_dao
        self.password_hasher: PasswordHasher = password_hasher

    @override
    async def __call__(self, command: ChangeUserPasswordCommand) -> User:
        with _tracer.start_as_current_span("user.change_password") as span:
            span.set_attribute("user.id", str(command.user_id))
            logger = _logger.bind(user_id=str(command.user_id))

            logger.info("changing_user_password")

            user = await self.user_dao.find_by_id(
                command.user_id, includes=[UserLoadEnum.STUDENT]
            )
            if user is None:
                logger.error("user_not_found")
                raise UserNotFoundException(command.user_id)

            try:
                self.password_hasher.verify(
                    user.password_hash, command.current_password.get_secret_value()
                )
            except VerifyMismatchError as e:
                logger.error("invalid_current_password")
                raise InvalidPasswordException(command.user_id) from e
            logger.info("password_verified")

            new_password_hash = self.password_hasher.hash(
                command.new_password.get_secret_value()
            )
            user.password_hash = new_password_hash
            await self.user_dao.save(user)
            await self.user_dao.commit()

            logger.info("user_password_changed")

            return User.from_persistent(user)
