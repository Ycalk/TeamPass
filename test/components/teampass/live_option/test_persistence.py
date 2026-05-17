from typing import ClassVar

import pytest
from dishka.entities.depends_marker import FromDishka
from sqlalchemy.ext.asyncio import AsyncSession
from teampass.live_option import LiveOptionBase, OptionDef

from development.pytest_inject import inject

from .conftest import SampleOption


@pytest.mark.asyncio
class TestLiveOptionPersistence:
    @inject
    async def test_save_and_sync(self, session: FromDishka[AsyncSession]) -> None:
        option = SampleOption(session)
        option.greeting = "Saved"
        option.max_retries = 42
        option.enabled = False
        option.ratio = 3.14

        await option.save()
        await option.commit()

        reloaded = await SampleOption(session).sync()

        assert reloaded.greeting == "Saved"
        assert reloaded.max_retries == 42
        assert reloaded.enabled is False
        assert reloaded.ratio == 3.14

    @inject
    async def test_sync_without_saved_data_keeps_defaults(
        self, session: FromDishka[AsyncSession]
    ) -> None:
        class FreshOption(LiveOptionBase):
            name: ClassVar[str] = "fresh_option_unsaved"

            value: OptionDef[int] = OptionDef(description="Значение", default_value=999)

        option = await FreshOption(session).sync()

        assert option.value == 999

    @inject
    async def test_save_updates_existing(
        self, session: FromDishka[AsyncSession]
    ) -> None:
        class UpdatableOption(LiveOptionBase):
            name: ClassVar[str] = "updatable_option"

            counter: OptionDef[int] = OptionDef(description="Счётчик", default_value=0)

        first = UpdatableOption(session)
        first.counter = 1
        await first.save()
        await first.commit()

        second = UpdatableOption(session)
        second.counter = 2
        await second.save()
        await second.commit()

        reloaded = await UpdatableOption(session).sync()
        assert reloaded.counter == 2

    @inject
    async def test_save_returns_self(self, session: FromDishka[AsyncSession]) -> None:
        option = SampleOption(session)
        result = await option.save()

        assert result is option
