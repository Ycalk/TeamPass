from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
from dishka import AsyncContainer, Provider, make_async_container
from teampass.database import DatabaseProvider
from teampass.media_storage import GetMediaMethod, MediaStorageProvider, SaveMediaMethod
from teampass.media_storage.s3 import IS3Client
from teampass.media_storage.settings import MediaStorageSettings
from teampass.media_storage.storage import MediaDAO
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


@pytest_asyncio.fixture
async def s3_client(request_container: AsyncContainer) -> IS3Client:
    return await request_container.get(IS3Client)


@pytest_asyncio.fixture
async def media_dao(request_container: AsyncContainer) -> MediaDAO:
    return await request_container.get(MediaDAO)


@pytest_asyncio.fixture
async def get_media_method(request_container: AsyncContainer) -> GetMediaMethod:
    return await request_container.get(GetMediaMethod)


@pytest_asyncio.fixture
async def save_media_method(request_container: AsyncContainer) -> SaveMediaMethod:
    return await request_container.get(SaveMediaMethod)


@pytest_asyncio.fixture
async def media_storage_settings(
    request_container: AsyncContainer,
) -> MediaStorageSettings:
    return await request_container.get(MediaStorageSettings)


@pytest.fixture
def test_png() -> bytes:
    current_dir = Path(__file__).resolve().parent
    with open(current_dir / "test.png", "rb") as f:
        file_bytes = f.read()
    return file_bytes
