from collections.abc import AsyncIterator

import pytest_asyncio
from dishka import AsyncContainer, Provider, make_async_container
from teampass.database import DatabaseProvider
from teampass.entrypoint import core


def test_sample():
    assert core is not None


@pytest_asyncio.fixture(scope="class")
async def app_container(
    test_database_provider: Provider,
) -> AsyncIterator[AsyncContainer]:
    container = make_async_container(DatabaseProvider(), test_database_provider)
    yield container
    await container.close()
