from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
from dishka import AsyncContainer, Provider, make_async_container
from teampass.database import DatabaseProvider
from teampass.media_storage import MediaStorageProvider
from teampass.report import (
    CreateReportMethod,
    GetReportMethod,
    ReportProvider,
    UpdateReportMethod,
    UploadMediaMethod,
)
from teampass.report.storage import ReportDAO
from teampass.user import UserProvider
from teampass.user.storage import StudentDAO, User, UserDAO


@pytest_asyncio.fixture(scope="class")
async def app_container(
    test_database_provider: Provider,
) -> AsyncIterator[AsyncContainer]:
    container = make_async_container(
        DatabaseProvider(),
        test_database_provider,
        UserProvider(),
        MediaStorageProvider(),
        ReportProvider(),
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
            student_id="report_test_student",
            first_name="Report",
            last_name="Tester",
            patronymic=None,
        )
        user = await user_dao.create(
            email="report_test@example.com",
            password_hash="hash",
            student_id=student.id,
        )
        await user_dao.commit()
    return user


@pytest_asyncio.fixture
async def report_dao(request_container: AsyncContainer) -> ReportDAO:
    return await request_container.get(ReportDAO)


@pytest_asyncio.fixture
async def user_dao(request_container: AsyncContainer) -> UserDAO:
    return await request_container.get(UserDAO)


@pytest_asyncio.fixture
async def create_report_method(
    request_container: AsyncContainer,
) -> CreateReportMethod:
    return await request_container.get(CreateReportMethod)


@pytest_asyncio.fixture
async def get_report_method(request_container: AsyncContainer) -> GetReportMethod:
    return await request_container.get(GetReportMethod)


@pytest_asyncio.fixture
async def update_report_method(
    request_container: AsyncContainer,
) -> UpdateReportMethod:
    return await request_container.get(UpdateReportMethod)


@pytest_asyncio.fixture
async def upload_media_method(
    request_container: AsyncContainer,
) -> UploadMediaMethod:
    return await request_container.get(UploadMediaMethod)


@pytest.fixture
def test_png() -> bytes:
    current_dir = Path(__file__).resolve().parent.parent / "media_storage"
    with open(current_dir / "test.png", "rb") as f:
        file_bytes = f.read()
    return file_bytes
