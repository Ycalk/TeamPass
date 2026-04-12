from typing import Annotated, Final, override

import structlog
from argon2 import PasswordHasher
from opentelemetry import trace
from pydantic import BaseModel, EmailStr, SecretStr, StringConstraints
from teampass.domain_core import DomainMethod
from teampass.user.dto import User
from teampass.user.storage import StudentDAO, UserDAO

from .exceptions import (
    EmailAlreadyExistsException,
    InvalidStudentDataException,
    StudentAlreadyRegisteredException,
    StudentNotFoundException,
)

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class RegisterUserCommand(BaseModel):
    email: EmailStr
    plain_password: Annotated[SecretStr, StringConstraints(min_length=8)]
    student_id: Annotated[str, StringConstraints(pattern=r"^\d+$")]
    first_name: str
    last_name: str
    patronymic: str | None


class RegisterUserMethod(DomainMethod[RegisterUserCommand, User]):
    def __init__(
        self,
        student_dao: StudentDAO,
        user_dao: UserDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        self.student_dao: StudentDAO = student_dao
        self.user_dao: UserDAO = user_dao
        self.password_hasher: PasswordHasher = password_hasher

    @override
    async def __call__(self, command: RegisterUserCommand) -> User:
        with _tracer.start_as_current_span("user.register") as span:
            span.set_attribute("user.email", command.email)
            span.set_attribute("user.student_id", command.student_id)
            span.set_attribute("user.first_name", command.first_name)
            span.set_attribute("user.last_name", command.last_name)
            span.set_attribute("user.patronymic", command.patronymic or "none")
            logger = _logger.bind(email=command.email, student_id=command.student_id)

            logger.info("registering_user")

            student = await self.student_dao.find_by_student_id(command.student_id)
            if student is None:
                raise StudentNotFoundException(command.student_id)
            if (
                student.first_name.lower() != command.first_name.lower()
                or student.last_name.lower() != command.last_name.lower()
                or (student.patronymic or "").lower()
                != (command.patronymic or "").lower()
            ):
                span.set_attribute("user.student.id", str(student.id))
                span.set_attribute("user.student.first_name", student.first_name)
                span.set_attribute("user.student.last_name", student.last_name)
                span.set_attribute(
                    "user.student.patronymic", student.patronymic or "none"
                )
                logger.error("invalid_student_data")
                raise InvalidStudentDataException(
                    command.student_id,
                    command.first_name,
                    command.last_name,
                    command.patronymic,
                )

            user = await self.user_dao.find_by_student_id(student.id)
            if user is not None:
                span.set_attribute("user.id", str(user.id))
                logger.error("student_already_registered")
                raise StudentAlreadyRegisteredException(command.student_id)

            user = await self.user_dao.find_by_email(command.email)
            if user is not None:
                span.set_attribute("user.id", str(user.id))
                logger.error("email_already_registered")
                raise EmailAlreadyExistsException(command.email)

            password_hash = self.password_hasher.hash(
                command.plain_password.get_secret_value()
            )
            user = await self.user_dao.create(
                email=command.email,
                password_hash=password_hash,
                student_id=student.id,
            )

            span.set_attribute("user.id", str(user.id))
            logger.info("user_registered")
            await self.user_dao.commit()
            return User.from_persistent(user)
