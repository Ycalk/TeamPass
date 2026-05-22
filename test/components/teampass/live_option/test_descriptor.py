import pytest
from dishka.entities.depends_marker import FromDishka
from sqlalchemy.ext.asyncio import AsyncSession
from teampass.live_option import OptionDef

from development.pytest_inject import inject

from .conftest import SampleOption


@pytest.mark.asyncio
class TestLiveOptionDescriptor:
    @inject
    async def test_set_and_get(self, session: FromDishka[AsyncSession]) -> None:
        option = SampleOption(session)

        option.greeting = "Привет"
        option.max_retries = 10
        option.enabled = False
        option.ratio = 1.5

        assert option.greeting == "Привет"
        assert option.max_retries == 10
        assert option.enabled is False
        assert option.ratio == 1.5

    async def test_class_level_access_returns_option_def(self) -> None:
        assert isinstance(SampleOption.greeting, OptionDef)
        assert isinstance(SampleOption.max_retries, OptionDef)
        assert isinstance(SampleOption.enabled, OptionDef)
        assert isinstance(SampleOption.ratio, OptionDef)
