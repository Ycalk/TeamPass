from html import escape
from typing import Literal, override

from ._base import BlockDataModel


class QuoteData(BlockDataModel):
    text: str
    caption: str
    alignment: Literal["left", "center"]

    @override
    def to_html(self) -> str:
        return f"<blockquote>{escape(self.text)}</blockquote> - {escape(self.caption)}"
