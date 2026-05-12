from typing import override
from uuid import UUID

from pydantic import BaseModel

from ._base import BlockDataModel


class ImageFile(BaseModel):
    id: UUID


class ImageFileWithURL(BaseModel):
    id: UUID
    url: str


class ImageData(BlockDataModel):
    file: ImageFile | ImageFileWithURL
    caption: str
    withBorder: bool
    withBackground: bool
    stretched: bool

    @override
    def to_html(self) -> str:
        if isinstance(self.file, ImageFile):
            raise RuntimeError("Image data does not contain url")

        return f'<img src="{self.file.url}" alt="{self.caption}" />'

    def clean_url(self) -> None:
        self.file = ImageFile(id=self.file.id)

    def add_url(self, url: str) -> None:
        self.file = ImageFileWithURL(id=self.file.id, url=url)
