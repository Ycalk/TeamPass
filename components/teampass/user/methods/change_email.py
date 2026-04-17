from typing import Final, override
from uuid import UUID

import structlog
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from opentelemetry import trace
from pydantic import BaseModel, EmailStr, SecretStr
from teampass.domain_core import DomainMethod
from teampass.user.dto import User
from teampass.user.storage import UserDAO, UserLoadEnum

from .exceptions import (
    EmailAlreadyExistsException,
    InvalidPasswordException,
    UserNotFoundException,
)

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class ChangeUserEmailPayload(BaseModel):
    new_email: EmailStr
    current_password: SecretStr


class ChangeUserEmailCommand(ChangeUserEmailPayload):
    user_id: UUID


class ChangeUserEmailMethod(DomainMethod[ChangeUserEmailCommand, User]):
    def __init__(
        self,
        user_dao: UserDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        self.user_dao: UserDAO = user_dao
        self.password_hasher: PasswordHasher = password_hasher

    @override
    async def __call__(self, command: ChangeUserEmailCommand) -> User:
        with _tracer.start_as_current_span("user.change_email") as span:
            span.set_attribute("user.id", str(command.user_id))
            span.set_attribute("user.new_email", command.new_email)
            logger = _logger.bind(
                user_id=str(command.user_id),
                new_email=command.new_email,
            )

            logger.info("changing_user_email")

            user = await self.user_dao.find_by_id(
                command.user_id, includes=[UserLoadEnum.STUDENT]
            )
            if user is None:
                logger.error("user_not_found")
                raise UserNotFoundException(command.user_id)

            existing_user = await self.user_dao.find_by_email(command.new_email)
            if existing_user is not None:
                span.set_attribute("user.existing_user.id", str(existing_user.id))
                logger.error("email_already_registered")
                raise EmailAlreadyExistsException(command.new_email)

            try:
                self.password_hasher.verify(
                    user.password_hash, command.current_password.get_secret_value()
                )
            except VerifyMismatchError as e:
                logger.error("invalid_current_password")
                raise InvalidPasswordException(command.user_id) from e
            logger.info("password_verified")

            user.email = command.new_email
            await self.user_dao.save(user)
            await self.user_dao.commit()

            logger.info("user_email_changed")

            return User.from_persistent(user)
