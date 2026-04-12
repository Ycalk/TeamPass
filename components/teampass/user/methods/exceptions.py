from uuid import UUID

from teampass.domain_core import (
    DomainConflictException,
    DomainForbiddenException,
    DomainNotFoundException,
    DomainUnauthorizedException,
)


class InvalidEmailOrPasswordException(DomainUnauthorizedException):
    def __init__(self, email: str) -> None:
        self.email: str = email
        super().__init__(f"Invalid email or password for email {email}")


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


class UserNotFoundException(DomainNotFoundException):
    def __init__(self, user_id: UUID) -> None:
        self.user_id: UUID = user_id
        super().__init__(f"User with ID {user_id} not found")


class EmailAlreadyExistsException(DomainConflictException):
    def __init__(self, email: str) -> None:
        self.email: str = email
        super().__init__(f"Email {email} is already registered")


class InvalidPasswordException(DomainForbiddenException):
    def __init__(self, user_id: UUID) -> None:
        self.user_id: UUID = user_id
        super().__init__(f"Invalid current password for user with ID {user_id}")
