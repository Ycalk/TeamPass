import pytest
from argon2 import PasswordHasher
from pydantic import SecretStr
from teampass.admin.methods.create import (
    AdminAlreadyExistsException,
    CreateAdminCommand,
    CreateAdminMethod,
)
from teampass.admin.storage import AdminDAO


@pytest.mark.asyncio
class TestCreateAdminMethod:
    async def test_create_admin_success(
        self,
        create_admin_method: CreateAdminMethod,
        admin_dao: AdminDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        command = CreateAdminCommand(
            username="admin1",
            plain_password=SecretStr("securepassword123"),
        )

        admin_dto = await create_admin_method(command)

        assert admin_dto is not None
        assert admin_dto.username == "admin1"

        admin_in_db = await admin_dao.find_by_username("admin1")
        assert admin_in_db is not None
        assert admin_in_db.id == admin_dto.id

        assert password_hasher.verify(admin_in_db.password_hash, "securepassword123")

    async def test_create_admin_already_exists(
        self,
        create_admin_method: CreateAdminMethod,
        admin_dao: AdminDAO,
        password_hasher: PasswordHasher,
    ) -> None:
        await admin_dao.create(
            username="existingadmin",
            password_hash=password_hasher.hash("somepassword"),
        )

        command = CreateAdminCommand(
            username="existingadmin",
            plain_password=SecretStr("securepassword123"),
        )

        with pytest.raises(AdminAlreadyExistsException) as exc_info:
            await create_admin_method(command)

        assert exc_info.value.username == "existingadmin"
