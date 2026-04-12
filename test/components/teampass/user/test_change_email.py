import uuid

import pytest
from argon2 import PasswordHasher
from pydantic import SecretStr
from teampass.user import (
    ChangeUserEmailCommand,
    ChangeUserEmailMethod,
    EmailAlreadyExistsException,
    InvalidPasswordException,
    UserNotFoundException,
)
from teampass.user.storage import StudentDAO, UserDAO


@pytest.mark.asyncio
class TestChangeEmailMethod:
    async def test_change_email_success(
        self,
        change_user_email_method: ChangeUserEmailMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        student = await student_dao.create(
            student_id="ce123",
            first_name="Ivan",
            last_name="Ivanov",
            patronymic="Ivanovich",
        )
        user = await user_dao.create(
            email="old@example.com",
            password_hash=password_hasher.hash("correctpassword"),
            student_id=student.id,
        )

        command = ChangeUserEmailCommand(
            user_id=user.id,
            new_email="new@example.com",
            current_password=SecretStr("correctpassword"),
        )
        updated_user = await change_user_email_method(command)

        assert updated_user is not None
        assert updated_user.email == "new@example.com"

        user_in_db = await user_dao.find_by_id_with_loaded_student(user.id)
        assert user_in_db is not None
        assert getattr(user_in_db, "email") == "new@example.com"

    async def test_change_email_user_not_found(
        self,
        change_user_email_method: ChangeUserEmailMethod,
    ) -> None:
        not_found_id = uuid.uuid4()
        command = ChangeUserEmailCommand(
            user_id=not_found_id,
            new_email="missing@example.com",
            current_password=SecretStr("correctpassword"),
        )

        with pytest.raises(UserNotFoundException) as exc_info:
            await change_user_email_method(command)

        assert exc_info.value.user_id == not_found_id

    async def test_change_email_invalid_password(
        self,
        change_user_email_method: ChangeUserEmailMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        student = await student_dao.create(
            student_id="ce124",
            first_name="Petr",
            last_name="Petrov",
            patronymic="Petrovich",
        )
        user = await user_dao.create(
            email="petr@example.com",
            password_hash=password_hasher.hash("correctpassword"),
            student_id=student.id,
        )

        command = ChangeUserEmailCommand(
            user_id=user.id,
            new_email="newpetr@example.com",
            current_password=SecretStr("wrongpassword"),
        )

        with pytest.raises(InvalidPasswordException) as exc_info:
            await change_user_email_method(command)

        assert exc_info.value.user_id == user.id

    async def test_change_email_already_exists(
        self,
        change_user_email_method: ChangeUserEmailMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        student1 = await student_dao.create(
            student_id="ce125",
            first_name="Alex",
            last_name="Alexeev",
            patronymic="Alexeevich",
        )
        await user_dao.create(
            email="taken@example.com",
            password_hash=password_hasher.hash("password123"),
            student_id=student1.id,
        )

        student2 = await student_dao.create(
            student_id="ce126",
            first_name="Bob",
            last_name="Bobov",
            patronymic="Bobovich",
        )
        user2 = await user_dao.create(
            email="bob@example.com",
            password_hash=password_hasher.hash("mypassword"),
            student_id=student2.id,
        )

        command = ChangeUserEmailCommand(
            user_id=user2.id,
            new_email="taken@example.com",
            current_password=SecretStr("mypassword"),
        )

        with pytest.raises(EmailAlreadyExistsException) as exc_info:
            await change_user_email_method(command)

        assert exc_info.value.email == "taken@example.com"
