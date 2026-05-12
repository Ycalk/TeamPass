from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel


class BlockDataModel(BaseModel, ABC):  # pyright: ignore[reportUnsafeMultipleInheritance]
    @abstractmethod
    def to_html(self) -> str:
        pass


class ReportBlock[T: str, TData: BlockDataModel](BaseModel):
    id: str
    type: T
    data: TData

    def to_html(self) -> str:
        return self.data.to_html()
