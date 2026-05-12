import asyncio
from typing import Final, override
from uuid import UUID

import structlog
from opentelemetry import trace
from pydantic import BaseModel
from teampass.domain_core import DomainMethod
from teampass.media_storage.methods import GetMediaCommand, GetMediaMethod
from teampass.report.dto import ReportContent
from teampass.report.dto.blocks.image import ImageData
from teampass.report.storage import ReportDAO

from .exceptions import ReportNotFoundException

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class GetReportCommand(BaseModel):
    report_id: UUID


class GetReportMethod(DomainMethod[GetReportCommand, ReportContent]):
    def __init__(
        self,
        report_dao: ReportDAO,
        get_media: GetMediaMethod,
    ) -> None:
        self.report_dao: ReportDAO = report_dao
        self.get_media: GetMediaMethod = get_media

    async def _add_url(self, image_data: ImageData, semaphore: asyncio.Semaphore):
        async with semaphore:
            media = await self.get_media(GetMediaCommand(media_id=image_data.file.id))
            image_data.add_url(media.url)

    @override
    async def __call__(self, command: GetReportCommand) -> ReportContent:
        with _tracer.start_as_current_span("report.get") as span:
            span.set_attribute("report.id", str(command.report_id))
            logger = _logger.bind(report_id=str(command.report_id))

            logger.info("fetching_report")

            report = await self.report_dao.find_by_id(command.report_id)
            if report is None:
                logger.error("report_not_found")
                raise ReportNotFoundException(command.report_id)

            report_data = ReportContent.model_validate(report.content)

            semaphore = asyncio.Semaphore(10)
            tasks = [
                self._add_url(block.data, semaphore)
                for block in report_data.blocks
                if isinstance(block.data, ImageData)
            ]
            await asyncio.gather(*tasks)

            logger.info("report_fetched")

            return report_data
