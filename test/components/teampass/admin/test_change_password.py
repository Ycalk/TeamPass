from uuid import uuid4

import pytest
from argon2 import PasswordHasher
from pydantic import SecretStr
from teampass.admin.methods.change_password import (
    AdminNotFoundException,
    ChangeAdminPasswordCommand,
    ChangeAdminPasswordMethod,
    InvalidPasswordException,
)
from teampass.admin.storage import AdminDAO


@pytest.mark.asyncio
class TestChangeAdminPasswordMethod:
    async def test_change_password_success(
        self,
        change_admin_password_method: ChangeAdminPasswordMethod,
        admin_dao: AdminDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        admin = await admin_dao.create(
            username="changepassadmin",
            password_hash=password_hasher.hash("oldpassword"),
        )

        command = ChangeAdminPasswordCommand(
            admin_id=admin.id,
            current_password=SecretStr("oldpassword"),
            new_password=SecretStr("newpassword123"),
        )

        admin_dto = await change_admin_password_method(command)

        assert admin_dto is not None
        assert admin_dto.username == "changepassadmin"

        admin_in_db = await admin_dao.find_by_username("changepassadmin")
        assert admin_in_db is not None
        assert password_hasher.verify(admin_in_db.password_hash, "newpassword123")

    async def test_change_password_admin_not_found(
        self,
        change_admin_password_method: ChangeAdminPasswordMethod,
    ) -> None:
        command = ChangeAdminPasswordCommand(
            admin_id=uuid4(),
            current_password=SecretStr("oldpassword"),
            new_password=SecretStr("newpassword123"),
        )

        with pytest.raises(AdminNotFoundException) as exc_info:
            await change_admin_password_method(command)

        assert exc_info.value.admin_id == command.admin_id

    async def test_change_password_invalid_current_password(
        self,
        change_admin_password_method: ChangeAdminPasswordMethod,
        admin_dao: AdminDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        admin = await admin_dao.create(
            username="invalidcurpassadmin",
            password_hash=password_hasher.hash("oldpassword"),
        )

        command = ChangeAdminPasswordCommand(
            admin_id=admin.id,
            current_password=SecretStr("wrongoldpassword"),
            new_password=SecretStr("newpassword123"),
        )

        with pytest.raises(InvalidPasswordException) as exc_info:
            await change_admin_password_method(command)

        assert exc_info.value.admin_id == admin.id
