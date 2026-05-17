from typing import ClassVar

import pytest
from dishka.entities.depends_marker import FromDishka
from sqlalchemy.ext.asyncio import AsyncSession
from teampass.live_option import LiveOptionBase, OptionDef
from teampass.live_option.core import (
    _LiveOptionStorage,  # pyright: ignore[reportPrivateUsage]
)

from development.pytest_inject import inject


@pytest.mark.asyncio
class TestLiveOptionIgnoresUnknownKeys:
    @inject
    async def test_sync_ignores_extra_keys_in_storage(
        self, session: FromDishka[AsyncSession]
    ) -> None:
        storage = _LiveOptionStorage(
            key="extra_keys_option",
            value={"known": 10, "unknown_field": "extra"},
        )
        session.add(storage)
        await session.flush()
        await session.commit()

        class PartialOption(LiveOptionBase):
            name: ClassVar[str] = "extra_keys_option"

            known: OptionDef[int] = OptionDef(
                description="Известное поле", default_value=0
            )

        option = await PartialOption(session).sync()

        assert option.known == 10
