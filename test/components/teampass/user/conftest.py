from collections.abc import AsyncIterator

import pytest_asyncio
from argon2 import PasswordHasher
from dishka import AsyncContainer, Provider, make_async_container
from teampass.database import DatabaseProvider
from teampass.user import (
    ChangeUserEmailMethod,
    ChangeUserPasswordMethod,
    LoginUserMethod,
    RegisterUserMethod,
    UpdateStudentProfileMethod,
    UserProvider,
)
from teampass.user.storage import StudentDAO, StudentProfileDAO, UserDAO


@pytest_asyncio.fixture(scope="class")
async def app_container(
    test_database_provider: Provider,
) -> AsyncIterator[AsyncContainer]:
    container = make_async_container(
        DatabaseProvider(), test_database_provider, UserProvider()
    )
    yield container
    await container.close()


@pytest_asyncio.fixture
async def password_hasher(request_container: AsyncContainer) -> PasswordHasher:
    return await request_container.get(PasswordHasher)


@pytest_asyncio.fixture
async def user_dao(request_container: AsyncContainer) -> UserDAO:
    return await request_container.get(UserDAO)


@pytest_asyncio.fixture
async def student_dao(request_container: AsyncContainer) -> StudentDAO:
    return await request_container.get(StudentDAO)


@pytest_asyncio.fixture
async def student_profile_dao(request_container: AsyncContainer) -> StudentProfileDAO:
    return await request_container.get(StudentProfileDAO)


@pytest_asyncio.fixture
async def register_user_method(request_container: AsyncContainer) -> RegisterUserMethod:
    return await request_container.get(RegisterUserMethod)


@pytest_asyncio.fixture
async def login_user_method(request_container: AsyncContainer) -> LoginUserMethod:
    return await request_container.get(LoginUserMethod)


@pytest_asyncio.fixture
async def change_user_email_method(
    request_container: AsyncContainer,
) -> ChangeUserEmailMethod:
    return await request_container.get(ChangeUserEmailMethod)


@pytest_asyncio.fixture
async def change_user_password_method(
    request_container: AsyncContainer,
) -> ChangeUserPasswordMethod:
    return await request_container.get(ChangeUserPasswordMethod)


@pytest_asyncio.fixture
async def update_student_profile_method(
    request_container: AsyncContainer,
) -> UpdateStudentProfileMethod:
    return await request_container.get(UpdateStudentProfileMethod)
