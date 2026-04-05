from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from dishka import AsyncContainer, Provider, make_async_container
from teampass.database.core import BaseDAOFactory, DatabaseProvider
from teampass.database.settings import DatabaseSettings


@pytest_asyncio.fixture(scope="class")
async def app_container(
    test_database_provider: Provider,
) -> AsyncIterator[AsyncContainer]:
    container = make_async_container(DatabaseProvider(), test_database_provider)
    yield container
    await container.close()


def test_base_dao_factory_cannot_be_instantiated():
    with pytest.raises(
        TypeError, match="Only subclasses of BaseDAOFactory can be instantiated"
    ):
        BaseDAOFactory(None, None)  # type: ignore # pyright: ignore


def test_base_dao_factory_subclass_can_be_instantiated():
    class MyDAOFactory(BaseDAOFactory):  # pyright: ignore
        def __init__(self):  # pyright: ignore
            pass

    factory = MyDAOFactory()
    assert factory is not None


def test_database_provider_url_generation():
    provider = DatabaseProvider()
    settings = DatabaseSettings(
        postgres_user="test_usr",
        postgres_password="test_password",
        postgres_host="localhost",
        postgres_port=5432,
        postgres_db="test_db",
    )

    url = provider.database_url(settings)
    assert url == "postgresql+asyncpg://test_usr:test_password@localhost:5432/test_db"
