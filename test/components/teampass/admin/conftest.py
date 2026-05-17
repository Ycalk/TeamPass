from collections.abc import AsyncIterator

import pytest_asyncio
from dishka import AsyncContainer, Provider, make_async_container
from teampass.admin.core import AdminProvider
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
