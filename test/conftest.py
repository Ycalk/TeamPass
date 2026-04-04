from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from dishka import AsyncContainer, Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import StaticPool
from teampass.database import BaseModel


def register_models() -> list[type]:
    from teampass.team.storage import Team
    from teampass.user.storage import Student, StudentProfile, User

    return [Student, StudentProfile, User, Team]


class TestDatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    async def engine(self) -> AsyncIterator[AsyncEngine]:
        register_models()
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=False,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        async with engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)
        yield engine
        await engine.dispose()


@pytest.fixture(scope="class")
def test_database_provider() -> TestDatabaseProvider:
    return TestDatabaseProvider()


@pytest_asyncio.fixture
async def request_container(
    app_container: AsyncContainer,
) -> AsyncIterator[AsyncContainer]:
    async with app_container() as request_container:
        yield request_container
