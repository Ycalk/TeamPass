import pytest
from argon2 import PasswordHasher
from pydantic import SecretStr
from teampass.admin.methods.login import (
    InvalidUsernameOrPasswordException,
    LoginAdminCommand,
    LoginAdminMethod,
)
from teampass.admin.storage import AdminDAO


@pytest.mark.asyncio
class TestLoginAdminMethod:
    async def test_login_success(
        self,
        login_admin_method: LoginAdminMethod,
        admin_dao: AdminDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        await admin_dao.create(
            username="loginadmin",
            password_hash=password_hasher.hash("correctpassword"),
        )

        command = LoginAdminCommand(
            username="loginadmin",
            plain_password=SecretStr("correctpassword"),
        )

        admin_dto = await login_admin_method(command)

        assert admin_dto is not None
        assert admin_dto.username == "loginadmin"

    async def test_login_invalid_username(
        self,
        login_admin_method: LoginAdminMethod,
    ) -> None:
        command = LoginAdminCommand(
            username="nonexistentadmin",
            plain_password=SecretStr("correctpassword"),
        )

        with pytest.raises(InvalidUsernameOrPasswordException) as exc_info:
            await login_admin_method(command)

        assert exc_info.value.username == "nonexistentadmin"

    async def test_login_invalid_password(
        self,
        login_admin_method: LoginAdminMethod,
        admin_dao: AdminDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        await admin_dao.create(
            username="invalidpassadmin",
            password_hash=password_hasher.hash("correctpassword"),
        )

        command = LoginAdminCommand(
            username="invalidpassadmin",
            plain_password=SecretStr("wrongpassword"),
        )

        with pytest.raises(InvalidUsernameOrPasswordException) as exc_info:
            await login_admin_method(command)

        assert exc_info.value.username == "invalidpassadmin"
