from collections.abc import AsyncIterator
from typing import ClassVar

import pytest_asyncio
from dishka import AsyncContainer, Provider, make_async_container
from sqlalchemy.ext.asyncio import AsyncSession
from teampass.database import DatabaseProvider
from teampass.live_option import LiveOptionBase, OptionDef


class SampleOption(LiveOptionBase):
    name: ClassVar[str] = "test_option"

    greeting: OptionDef[str] = OptionDef(
        description="Приветственное сообщение", default_value="Hello"
    )
    max_retries: OptionDef[int] = OptionDef(
        description="Максимальное количество повторов", default_value=3
    )
    enabled: OptionDef[bool] = OptionDef(
        description="Включен ли модуль", default_value=True
    )
    ratio: OptionDef[float] = OptionDef(
        description="Коэффициент расчёта", default_value=0.75
    )


@pytest_asyncio.fixture(scope="class")
async def app_container(
    test_database_provider: Provider,
) -> AsyncIterator[AsyncContainer]:
    container = make_async_container(DatabaseProvider(), test_database_provider)
    yield container
    await container.close()


@pytest_asyncio.fixture
async def session(request_container: AsyncContainer) -> AsyncSession:
    return await request_container.get(AsyncSession)
