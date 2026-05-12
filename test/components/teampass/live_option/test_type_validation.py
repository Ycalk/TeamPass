from typing import ClassVar

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from teampass.live_option import LiveOptionBase, OptionDef
from teampass.live_option.core import (
    _LiveOptionStorage,  # pyright: ignore[reportPrivateUsage]
)


@pytest.mark.asyncio
class TestLiveOptionTypeValidation:
    async def test_sync_raises_on_type_mismatch(self, session: AsyncSession) -> None:
        storage = _LiveOptionStorage(
            key="type_mismatch_option",
            value={"score": "not_an_int"},
        )
        session.add(storage)
        await session.flush()
        await session.commit()

        class TypeMismatchOption(LiveOptionBase):
            name: ClassVar[str] = "type_mismatch_option"

            score: OptionDef[int] = OptionDef(description="Очки", default_value=0)

        with pytest.raises(TypeError, match="Expected int, got str"):
            await TypeMismatchOption(session).sync()
