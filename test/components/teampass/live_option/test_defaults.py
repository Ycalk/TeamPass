import pytest
from dishka.entities.depends_marker import FromDishka
from sqlalchemy.ext.asyncio import AsyncSession

from development.pytest_inject import inject

from .conftest import SampleOption


@pytest.mark.asyncio
class TestLiveOptionDefaults:
    @inject
    async def test_default_values(self, session: FromDishka[AsyncSession]) -> None:
        option = SampleOption(session)

        assert option.greeting == "Hello"
        assert option.max_retries == 3
        assert option.enabled is True
        assert option.ratio == 0.75

    @inject
    async def test_options_registered(self, session: FromDishka[AsyncSession]) -> None:
        option = SampleOption(session)

        option_names = {opt.name for opt in option.__options__}
        assert option_names == {"greeting", "max_retries", "enabled", "ratio"}
