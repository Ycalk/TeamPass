import pytest
from argon2 import PasswordHasher
from pydantic import SecretStr
from teampass.user import (
    InvalidEmailOrPasswordException,
    LoginUserCommand,
    LoginUserMethod,
)
from teampass.user.storage import StudentDAO, UserDAO


@pytest.mark.asyncio
class TestLoginMethod:
    async def test_login_success(
        self,
        login_user_method: LoginUserMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        student = await student_dao.create(
            student_id="12345",
            first_name="Ivan",
            last_name="Ivanov",
            patronymic="Ivanovich",
        )
        await user_dao.create(
            email="ivan@example.com",
            password_hash=password_hasher.hash("password123"),
            student_id=student.id,
        )

        command = LoginUserCommand(
            email="ivan@example.com",
            plain_password=SecretStr("password123"),
        )

        user_dto = await login_user_method(command)

        assert user_dto is not None
        assert user_dto.email == "ivan@example.com"
        assert user_dto.student is not None
        assert user_dto.student.student_id == "12345"

    async def test_login_invalid_email(
        self,
        login_user_method: LoginUserMethod,
    ) -> None:
        command = LoginUserCommand(
            email="notfound@example.com",
            plain_password=SecretStr("password123"),
        )

        with pytest.raises(InvalidEmailOrPasswordException) as exc_info:
            await login_user_method(command)

        assert exc_info.value.email == "notfound@example.com"

    async def test_login_invalid_password(
        self,
        login_user_method: LoginUserMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        student = await student_dao.create(
            student_id="12346",
            first_name="Petr",
            last_name="Petrov",
            patronymic="Petrovich",
        )
        await user_dao.create(
            email="petr@example.com",
            password_hash=password_hasher.hash("correctpassword"),
            student_id=student.id,
        )

        command = LoginUserCommand(
            email="petr@example.com",
            plain_password=SecretStr("wrongpassword"),
        )

        with pytest.raises(InvalidEmailOrPasswordException) as exc_info:
            await login_user_method(command)

        assert exc_info.value.email == "petr@example.com"
