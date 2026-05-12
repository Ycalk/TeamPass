import pytest
from teampass.live_option import LiveOptionBase, OptionDef


@pytest.mark.asyncio
class TestLiveOptionSubclassValidation:
    async def test_subclass_without_name_raises(self) -> None:
        with pytest.raises(TypeError, match="must define a 'name' ClassVar"):

            class BadOption(LiveOptionBase):  # pyright: ignore[reportUnusedClass]
                value: OptionDef[int] = OptionDef(description="Тест", default_value=0)
