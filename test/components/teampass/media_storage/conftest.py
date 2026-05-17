from collections.abc import AsyncIterator

import pytest_asyncio
from dishka import AsyncContainer, Provider, make_async_container
from teampass.database import DatabaseProvider
from teampass.media_storage import MediaStorageProvider
from teampass.user import UserProvider
from teampass.user.storage import StudentDAO, User, UserDAO


@pytest_asyncio.fixture(scope="class")
async def app_container(
    test_database_provider: Provider,
) -> AsyncIterator[AsyncContainer]:
    container = make_async_container(
        DatabaseProvider(),
        test_database_provider,
        MediaStorageProvider(),
        UserProvider(),
    )
    yield container
    await container.close()


@pytest_asyncio.fixture(scope="class")
async def user(
    app_container: AsyncContainer,
) -> User:
    async with app_container() as request_container:
        student_dao = await request_container.get(StudentDAO)
        user_dao = await request_container.get(UserDAO)
        student = await student_dao.create(
            student_id="123",
            first_name="Ivan",
            last_name="Ivanov",
            patronymic="Ivanovich",
        )
        user = await user_dao.create(
            email="example@example.com",
            password_hash="password_hash",
            student_id=student.id,
        )
        await user_dao.commit()
    return user
