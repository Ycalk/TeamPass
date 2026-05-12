import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from .conftest import SampleOption


@pytest.mark.asyncio
class TestLiveOptionDefaults:
    async def test_default_values(self, session: AsyncSession) -> None:
        option = SampleOption(session)

        assert option.greeting == "Hello"
        assert option.max_retries == 3
        assert option.enabled is True
        assert option.ratio == 0.75

    async def test_options_registered(self, session: AsyncSession) -> None:
        option = SampleOption(session)

        option_names = {opt.name for opt in option.__options__}
        assert option_names == {"greeting", "max_retries", "enabled", "ratio"}
