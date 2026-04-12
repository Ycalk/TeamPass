import uuid

import pytest
from argon2 import PasswordHasher
from pydantic import ValidationError
from teampass.user import (
    UpdateStudentProfileCommand,
    UpdateStudentProfileMethod,
    UserNotFoundException,
)
from teampass.user.storage import StudentDAO, UserDAO


@pytest.mark.asyncio
class TestUpdateStudentProfileMethod:
    async def test_update_profile_success_all_fields(
        self,
        update_student_profile_method: UpdateStudentProfileMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        student = await student_dao.create(
            student_id="up123",
            first_name="Ivan",
            last_name="Ivanov",
            patronymic="Ivanovich",
        )
        user = await user_dao.create(
            email="up@example.com",
            password_hash=password_hasher.hash("password123"),
            student_id=student.id,
        )

        command = UpdateStudentProfileCommand(
            user_id=user.id,
            telegram_username="ivan_tg",
            vk_profile_link="https://vk.com/ivan.ivanov123",
            phone_number="+79998887766",
            strengths_text="Python, SQL",
            weaknesses_text="C++",
        )

        profile_dto = await update_student_profile_method(command)
        assert profile_dto is not None
        assert profile_dto.telegram_username == "ivan_tg"
        assert profile_dto.vk_profile_link == "https://vk.com/ivan.ivanov123"
        assert profile_dto.phone_number == "+79998887766"
        assert profile_dto.strengths_text == "Python, SQL"
        assert profile_dto.weaknesses_text == "C++"

    async def test_update_profile_success_partial_fields_and_reset(
        self,
        update_student_profile_method: UpdateStudentProfileMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        student = await student_dao.create(
            student_id="up124",
            first_name="Petr",
            last_name="Petrov",
            patronymic="Petrovich",
        )
        user = await user_dao.create(
            email="uppetr@example.com",
            password_hash=password_hasher.hash("password123"),
            student_id=student.id,
        )

        # First update to set data
        command1 = UpdateStudentProfileCommand(
            user_id=user.id,
            telegram_username="petr_tg",
            vk_profile_link="https://vk.com/petr.petrov",
        )
        await update_student_profile_method(command1)

        # Second update to reset vk_profile_link and leave telegram_username untouched
        command2 = UpdateStudentProfileCommand(
            user_id=user.id,
            vk_profile_link="",  # Should reset to None
            telegram_username=None,  # Should leave untouched
            strengths_text="Go",
        )
        profile_dto = await update_student_profile_method(command2)

        assert profile_dto.telegram_username == "petr_tg"
        assert profile_dto.vk_profile_link is None
        assert profile_dto.strengths_text == "Go"

    async def test_update_profile_user_not_found(
        self,
        update_student_profile_method: UpdateStudentProfileMethod,
    ) -> None:
        not_found_id = uuid.uuid4()
        command = UpdateStudentProfileCommand(
            user_id=not_found_id,
            telegram_username="ghost",
        )

        with pytest.raises(UserNotFoundException) as exc_info:
            await update_student_profile_method(command)

        assert exc_info.value.user_id == not_found_id

    async def test_update_profile_validation_telegram_username(self) -> None:
        id_ = uuid.uuid4()
        # Invalid chars
        with pytest.raises(ValidationError):
            UpdateStudentProfileCommand(user_id=id_, telegram_username="tg@user")
        # Too short
        with pytest.raises(ValidationError):
            UpdateStudentProfileCommand(user_id=id_, telegram_username="abcd")
        # Valid
        cmd = UpdateStudentProfileCommand(user_id=id_, telegram_username="abcde")
        assert cmd.telegram_username == "abcde"

    async def test_update_profile_validation_vk_link(self) -> None:
        id_ = uuid.uuid4()
        # Invalid prefix
        with pytest.raises(ValidationError):
            UpdateStudentProfileCommand(
                user_id=id_, vk_profile_link="https://facebook.com/id"
            )
        # Invalid characters
        with pytest.raises(ValidationError):
            UpdateStudentProfileCommand(
                user_id=id_, vk_profile_link="https://vk.com/id!@#"
            )
        # Too short
        with pytest.raises(ValidationError):
            UpdateStudentProfileCommand(
                user_id=id_, vk_profile_link="https://vk.com/abcd"
            )
        # Valid
        cmd = UpdateStudentProfileCommand(
            user_id=id_, vk_profile_link="https://vk.com/abcde"
        )
        assert cmd.vk_profile_link == "https://vk.com/abcde"

    async def test_update_profile_validation_phone_number(self) -> None:
        id_ = uuid.uuid4()
        # Invalid format (letters)
        with pytest.raises(ValidationError):
            UpdateStudentProfileCommand(user_id=id_, phone_number="phone123")
        # Too short
        with pytest.raises(ValidationError):
            UpdateStudentProfileCommand(user_id=id_, phone_number="+123456789")
        # Valid
        cmd = UpdateStudentProfileCommand(user_id=id_, phone_number="+1234567890")
        assert cmd.phone_number == "+1234567890"
