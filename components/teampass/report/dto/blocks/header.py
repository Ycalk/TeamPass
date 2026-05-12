from html import escape
from typing import override

from ._base import BlockDataModel


class HeaderData(BlockDataModel):
    text: str
    level: int

    @override
    def to_html(self) -> str:
        return f"<h{self.level}>{escape(self.text)}</h{self.level}>"
