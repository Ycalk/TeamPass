from typing import Any, override

import nh3

from ._base import BlockDataModel


class TextData(BlockDataModel):
    text: str

    @override
    def to_html(self) -> str:
        allowed_tags = {"b", "i", "u", "a", "mark", "code", "span", "br"}
        allowed_attributes: dict[str, Any] = {
            "a": {"href", "target"},
            "span": {"class"},
            "u": {"class"},
            "mark": {"class"},
        }
        return nh3.clean(self.text, tags=allowed_tags, attributes=allowed_attributes)
