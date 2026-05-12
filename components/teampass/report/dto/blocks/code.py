from html import escape
from typing import override

from ._base import BlockDataModel


class CodeData(BlockDataModel):
    code: str

    @override
    def to_html(self) -> str:
        return f"<pre><code>{escape(self.code)}</code></pre>"
