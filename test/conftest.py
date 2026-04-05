import sys
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from dishka import AsyncContainer, Provider, Scope, provide
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool
from teampass.database import BaseModel
from teampass.database.core import DatabaseUrl
from teampass.migrator import run as run_migrations


class TestDatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    async def engine(self, database_url: DatabaseUrl) -> AsyncIterator[AsyncEngine]:
        engine = create_async_engine(
            database_url,
            echo=False,
            poolclass=NullPool,
            connect_args={
                "server_settings": {
                    "timezone": "UTC",
                }
            },
            isolation_level="READ COMMITTED",
        )
        try:
            yield engine
        finally:
            await engine.dispose()


@pytest_asyncio.fixture(scope="class", autouse=True)
async def clean_database(app_container: AsyncContainer):
    engine = await app_container.get(AsyncEngine)
    tables = [f'"{table.name}"' for table in BaseModel.metadata.sorted_tables]
    if tables:
        truncate_query = f"TRUNCATE TABLE {', '.join(tables)} CASCADE;"
        async with engine.begin() as conn:
            await conn.execute(text(truncate_query))


@pytest.fixture(scope="class")
def test_database_provider() -> TestDatabaseProvider:
    return TestDatabaseProvider()


@pytest.fixture(scope="session", autouse=True)
def test_database_migrations() -> None:
    sys.argv = ["alembic", "upgrade", "head"]
    run_migrations()


@pytest_asyncio.fixture
async def request_container(
    app_container: AsyncContainer,
) -> AsyncIterator[AsyncContainer]:
    async with app_container() as request_container:
        yield request_container
