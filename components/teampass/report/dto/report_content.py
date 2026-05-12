from pydantic import BaseModel

from .blocks import AnyReportBlock


class ReportContent(BaseModel):
    time: int
    blocks: list[AnyReportBlock]
    version: str

    def to_html(self) -> str:
        return "".join(block.to_html() for block in self.blocks)
