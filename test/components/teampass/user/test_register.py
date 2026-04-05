import pytest
from argon2 import PasswordHasher
from pydantic import SecretStr
from teampass.user.methods.register import (
    EmailAlreadyRegisteredException,
    InvalidStudentDataException,
    RegisterUserCommand,
    RegisterUserMethod,
    StudentAlreadyRegisteredException,
    StudentNotFoundException,
)
from teampass.user.storage import StudentDAO, UserDAO


@pytest.mark.asyncio
class TestRegisterMethod:
    async def test_register_success(
        self,
        register_user_method: RegisterUserMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        await student_dao.create(
            student_id="12345",
            first_name="Ivan",
            last_name="Ivanov",
            patronymic="Ivanovich",
        )

        command = RegisterUserCommand(
            email="ivan@example.com",
            plain_password=SecretStr("password123"),
            student_id="12345",
            first_name="Ivan",
            last_name="Ivanov",
            patronymic="Ivanovich",
        )

        user_dto = await register_user_method(command)

        assert user_dto is not None
        assert user_dto.email == "ivan@example.com"

        user_in_db = await user_dao.find_by_email("ivan@example.com")
        assert user_in_db is not None
        assert user_in_db.id == user_dto.id

        assert password_hasher.verify(user_in_db.password_hash, "password123")

    async def test_register_success_without_patronymic(
        self,
        register_user_method: RegisterUserMethod,
        student_dao: StudentDAO,
    ) -> None:
        await student_dao.create(
            student_id="123456",
            first_name="Ivan",
            last_name="Ivanov",
            patronymic=None,
        )

        command = RegisterUserCommand(
            email="ivan_np@example.com",
            plain_password=SecretStr("password123"),
            student_id="123456",
            first_name="Ivan",
            last_name="Ivanov",
            patronymic=None,
        )

        user_dto = await register_user_method(command)
        assert user_dto is not None

    async def test_register_student_not_found(
        self,
        register_user_method: RegisterUserMethod,
    ) -> None:
        command = RegisterUserCommand(
            email="notfound@example.com",
            plain_password=SecretStr("password123"),
            student_id="99999",
            first_name="Ivan",
            last_name="Ivanov",
            patronymic="Ivanovich",
        )

        with pytest.raises(StudentNotFoundException) as exc_info:
            await register_user_method(command)

        assert exc_info.value.student_id == "99999"

    async def test_register_invalid_student_data(
        self,
        register_user_method: RegisterUserMethod,
        student_dao: StudentDAO,
    ) -> None:
        await student_dao.create(
            student_id="12347",
            first_name="Ivan",
            last_name="Ivanov",
            patronymic="Ivanovich",
        )

        command = RegisterUserCommand(
            email="invalid@example.com",
            plain_password=SecretStr("password123"),
            student_id="12347",
            first_name="Petr",
            last_name="Ivanov",
            patronymic="Ivanovich",
        )

        with pytest.raises(InvalidStudentDataException) as exc_info:
            await register_user_method(command)

        assert exc_info.value.student_id == "12347"

    async def test_register_student_already_registered(
        self,
        register_user_method: RegisterUserMethod,
        student_dao: StudentDAO,
    ) -> None:
        await student_dao.create(
            student_id="12348",
            first_name="Ivan",
            last_name="Ivanov",
            patronymic="Ivanovich",
        )

        command = RegisterUserCommand(
            email="first@example.com",
            plain_password=SecretStr("password123"),
            student_id="12348",
            first_name="Ivan",
            last_name="Ivanov",
            patronymic="Ivanovich",
        )

        await register_user_method(command)

        command2 = RegisterUserCommand(
            email="second@example.com",
            plain_password=SecretStr("password123"),
            student_id="12348",
            first_name="Ivan",
            last_name="Ivanov",
            patronymic="Ivanovich",
        )

        with pytest.raises(StudentAlreadyRegisteredException) as exc_info:
            await register_user_method(command2)

        assert exc_info.value.student_id == "12348"

    async def test_register_email_already_registered(
        self,
        register_user_method: RegisterUserMethod,
        student_dao: StudentDAO,
    ) -> None:
        await student_dao.create(
            student_id="12349",
            first_name="Ivan",
            last_name="Ivanov",
            patronymic="Ivanovich",
        )

        await student_dao.create(
            student_id="123410",
            first_name="Petr",
            last_name="Petrov",
            patronymic="Petrovich",
        )

        command1 = RegisterUserCommand(
            email="shared@example.com",
            plain_password=SecretStr("password123"),
            student_id="12349",
            first_name="Ivan",
            last_name="Ivanov",
            patronymic="Ivanovich",
        )
        await register_user_method(command1)

        command2 = RegisterUserCommand(
            email="shared@example.com",
            plain_password=SecretStr("password123"),
            student_id="123410",
            first_name="Petr",
            last_name="Petrov",
            patronymic="Petrovich",
        )

        with pytest.raises(EmailAlreadyRegisteredException) as exc_info:
            await register_user_method(command2)

        assert exc_info.value.email == "shared@example.com"
