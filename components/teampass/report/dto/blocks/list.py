from __future__ import annotations

from html import escape
from typing import Annotated, Literal, override

from pydantic import BaseModel, Field

from ._base import BlockDataModel


class OrderedMeta(BaseModel):
    start: int = 1
    counterType: Literal[
        "numeric", "lower-roman", "upper-roman", "lower-alpha", "upper-alpha"
    ] = "numeric"


class UnorderedMeta(BaseModel):
    pass


class ChecklistMeta(BaseModel):
    checked: bool


class ListItem[TMeta: BaseModel](BaseModel):
    content: str
    meta: TMeta
    items: list[ListItem[TMeta]] = Field(default_factory=list)


class OrderedListData(BlockDataModel):
    style: Literal["ordered"]
    meta: OrderedMeta
    items: list[ListItem[OrderedMeta]]

    @override
    def to_html(self) -> str:
        return self._generate_html(self.items, self.meta)

    def _generate_html(
        self, items: list[ListItem[OrderedMeta]], meta: OrderedMeta
    ) -> str:
        type_map = {
            "numeric": "1",
            "lower-roman": "i",
            "upper-roman": "I",
            "lower-alpha": "a",
            "upper-alpha": "A",
        }
        ol_type = type_map.get(meta.counterType, "1")
        start_attr = f' start="{meta.start}"' if meta.start != 1 else ""
        result: list[str] = []
        for item in items:
            inner_html = (
                self._generate_html(item.items, item.meta) if item.items else ""
            )
            result.append(f"<li>{escape(item.content)}{inner_html}</li>")

        return f'<ol type="{ol_type}"{start_attr}>{"".join(result)}</ol>'


class UnorderedListData(BlockDataModel):
    style: Literal["unordered"]
    meta: UnorderedMeta
    items: list[ListItem[UnorderedMeta]]

    @override
    def to_html(self) -> str:
        return self._generate_html(self.items)

    def _generate_html(self, items: list[ListItem[UnorderedMeta]]) -> str:
        result: list[str] = []
        for item in items:
            inner_html = self._generate_html(item.items) if item.items else ""
            result.append(f"<li>{escape(item.content)}{inner_html}</li>")

        return f"<ul>{''.join(result)}</ul>"


class ChecklistListData(BlockDataModel):
    style: Literal["checklist"]
    meta: ChecklistMeta
    items: list[ListItem[ChecklistMeta]]

    @override
    def to_html(self) -> str:
        return self._generate_html(self.items)

    def _generate_html(self, items: list[ListItem[ChecklistMeta]]) -> str:
        result: list[str] = []
        for item in items:
            checked_attr = "checked" if item.meta.checked else ""
            checkbox = f'<input type="checkbox" {checked_attr} disabled />'

            inner_html = self._generate_html(item.items) if item.items else ""
            result.append(f"<li>{checkbox} {escape(item.content)}{inner_html}</li>")

        return f'<ul class="checklist">{"".join(result)}</ul>'


ListData = Annotated[
    OrderedListData | UnorderedListData | ChecklistListData,
    Field(discriminator="style"),
]
