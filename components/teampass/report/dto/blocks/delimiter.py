from typing import override

from ._base import BlockDataModel


class DelimiterData(BlockDataModel):
    @override
    def to_html(self) -> str:
        return "<br/>"
