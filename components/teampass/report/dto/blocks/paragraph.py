from html import escape
from typing import override

from ._base import BlockDataModel


class ParagraphData(BlockDataModel):
    text: str

    @override
    def to_html(self) -> str:
        return f"<p>{escape(self.text)}</p>"
