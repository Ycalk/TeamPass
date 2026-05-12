from typing import Annotated, Literal

from pydantic import Field

from ._base import BlockDataModel, ReportBlock
from .code import CodeData
from .delimiter import DelimiterData
from .header import HeaderData
from .image import ImageData
from .list import ListData
from .paragraph import ParagraphData
from .quote import QuoteData
from .text import TextData

AnyReportBlock = Annotated[
    ReportBlock[Literal["code"], CodeData]
    | ReportBlock[Literal["delimiter"], DelimiterData]
    | ReportBlock[Literal["header"], HeaderData]
    | ReportBlock[Literal["image"], ImageData]
    | ReportBlock[Literal["list"], ListData]
    | ReportBlock[Literal["paragraph"], ParagraphData]
    | ReportBlock[Literal["quote"], QuoteData]
    | ReportBlock[Literal["text"], TextData],
    Field(discriminator="type"),
]

__all__ = [
    "BlockDataModel",
    "ReportBlock",
    "AnyReportBlock",
    "CodeData",
    "DelimiterData",
    "HeaderData",
    "ImageData",
    "ListData",
    "ParagraphData",
    "QuoteData",
    "TextData",
]
