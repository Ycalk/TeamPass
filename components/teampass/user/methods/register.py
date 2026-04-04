from typing import Annotated, Final, override

import structlog
from argon2 import PasswordHasher
from opentelemetry import trace
from pydantic import BaseModel, EmailStr, SecretStr, StringConstraints
from teampass.domain_core import (
    DomainConflictException,
    DomainForbiddenException,
    DomainMethod,
    DomainNotFoundException,
)
from teampass.user.dto import User
from teampass.user.storage import StudentDAO, UserDAO

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class StudentNotFoundException(DomainNotFoundException):
    def __init__(self, student_id: str) -> None:
        self.student_id: str = student_id
        super().__init__(f"Student with ID {student_id} not found")


class InvalidStudentDataException(DomainForbiddenException):
    def __init__(
        self,
        student_id: str,
        first_name: str,
        last_name: str,
        patronymic: str | None,
    ) -> None:
        self.student_id: str = student_id
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.patronymic: str | None = patronymic
        super().__init__(
            f"Invalid student data for student with ID {student_id}: "
            + f"{first_name} {last_name} {patronymic or ''}"
        )


class StudentAlreadyRegisteredException(DomainConflictException):
    def __init__(self, student_id: str) -> None:
        self.student_id: str = student_id
        super().__init__(f"Student with ID {student_id} already registered")


class EmailAlreadyRegisteredException(DomainConflictException):
    def __init__(self, email: str) -> None:
        self.email: str = email
        super().__init__(f"Email {email} already registered")


class RegisterUserCommand(BaseModel):
    email: EmailStr
    plain_password: Annotated[SecretStr, StringConstraints(min_length=8)]
    student_id: str
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
        with _tracer.start_as_current_span("register_user") as span:
            span.set_attribute("email", command.email)
            span.set_attribute("student_id", command.student_id)
            span.set_attribute("first_name", command.first_name)
            span.set_attribute("last_name", command.last_name)
            span.set_attribute("patronymic", command.patronymic or "none")
            logger = _logger.bind(email=command.email, student_id=command.student_id)

            logger.info("registering_user")

            student = await self.student_dao.find_by_student_id(command.student_id)
            if student is None:
                raise StudentNotFoundException(command.student_id)
            if (
                student.first_name != command.first_name
                or student.last_name != command.last_name
                or student.patronymic != command.patronymic
            ):
                span.set_attribute("student.id", str(student.id))
                span.set_attribute("student.first_name", student.first_name)
                span.set_attribute("student.last_name", student.last_name)
                span.set_attribute("student.patronymic", student.patronymic or "none")
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
                raise EmailAlreadyRegisteredException(command.email)

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
            return User.from_persistent(user)
