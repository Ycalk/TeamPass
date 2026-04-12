import uuid

import pytest
from argon2 import PasswordHasher
from pydantic import SecretStr, ValidationError
from teampass.user import (
    ChangeUserPasswordCommand,
    ChangeUserPasswordMethod,
    InvalidPasswordException,
    UserNotFoundException,
)
from teampass.user.storage import StudentDAO, UserDAO


@pytest.mark.asyncio
class TestChangePasswordMethod:
    async def test_change_password_success(
        self,
        change_user_password_method: ChangeUserPasswordMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        student = await student_dao.create(
            student_id="cp123",
            first_name="Ivan",
            last_name="Ivanov",
            patronymic="Ivanovich",
        )
        user = await user_dao.create(
            email="pw@example.com",
            password_hash=password_hasher.hash("correctpassword"),
            student_id=student.id,
        )

        command = ChangeUserPasswordCommand(
            user_id=user.id,
            current_password=SecretStr("correctpassword"),
            new_password=SecretStr("newstrongpassword"),
        )
        updated_user = await change_user_password_method(command)

        assert updated_user is not None

        user_in_db = await user_dao.find_by_id_with_loaded_student(user.id)
        assert user_in_db is not None
        assert password_hasher.verify(user_in_db.password_hash, "newstrongpassword")

    async def test_change_password_user_not_found(
        self,
        change_user_password_method: ChangeUserPasswordMethod,
    ) -> None:
        not_found_id = uuid.uuid4()
        command = ChangeUserPasswordCommand(
            user_id=not_found_id,
            current_password=SecretStr("correctpassword"),
            new_password=SecretStr("newstrongpassword"),
        )

        with pytest.raises(UserNotFoundException) as exc_info:
            await change_user_password_method(command)

        assert exc_info.value.user_id == not_found_id

    async def test_change_password_invalid_current_password(
        self,
        change_user_password_method: ChangeUserPasswordMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        student = await student_dao.create(
            student_id="cp124",
            first_name="Petr",
            last_name="Petrov",
            patronymic="Petrovich",
        )
        user = await user_dao.create(
            email="pw_petr@example.com",
            password_hash=password_hasher.hash("correctpassword"),
            student_id=student.id,
        )

        command = ChangeUserPasswordCommand(
            user_id=user.id,
            current_password=SecretStr("wrongpassword"),
            new_password=SecretStr("newstrongpassword"),
        )

        with pytest.raises(InvalidPasswordException) as exc_info:
            await change_user_password_method(command)

        assert exc_info.value.user_id == user.id

    async def test_change_password_validation_length(self) -> None:
        id_ = uuid.uuid4()
        with pytest.raises(ValidationError) as exc_info:
            ChangeUserPasswordCommand(
                user_id=id_,
                current_password=SecretStr("correctpassword"),
                new_password=SecretStr("short"),
            )
        assert exc_info.value.error_count() > 0
