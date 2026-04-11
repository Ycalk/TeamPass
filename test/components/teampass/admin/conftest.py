from collections.abc import AsyncIterator

import pytest_asyncio
from argon2 import PasswordHasher
from dishka import AsyncContainer, Provider, make_async_container
from teampass.admin.core import AdminProvider
from teampass.admin.methods.change_password import ChangeAdminPasswordMethod
from teampass.admin.methods.create import CreateAdminMethod
from teampass.admin.methods.login import LoginAdminMethod
from teampass.admin.storage import AdminDAO
from teampass.database import DatabaseProvider


@pytest_asyncio.fixture(scope="class")
async def app_container(
    test_database_provider: Provider,
) -> AsyncIterator[AsyncContainer]:
    container = make_async_container(
        DatabaseProvider(), test_database_provider, AdminProvider()
    )
    yield container
    await container.close()


@pytest_asyncio.fixture
async def password_hasher(request_container: AsyncContainer) -> PasswordHasher:
    return await request_container.get(PasswordHasher)


@pytest_asyncio.fixture
async def admin_dao(request_container: AsyncContainer) -> AdminDAO:
    return await request_container.get(AdminDAO)


@pytest_asyncio.fixture
async def create_admin_method(request_container: AsyncContainer) -> CreateAdminMethod:
    return await request_container.get(CreateAdminMethod)


@pytest_asyncio.fixture
async def login_admin_method(request_container: AsyncContainer) -> LoginAdminMethod:
    return await request_container.get(LoginAdminMethod)


@pytest_asyncio.fixture
async def change_admin_password_method(
    request_container: AsyncContainer,
) -> ChangeAdminPasswordMethod:
    return await request_container.get(ChangeAdminPasswordMethod)
