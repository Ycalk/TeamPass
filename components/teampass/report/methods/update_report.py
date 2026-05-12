from typing import Final, override
from uuid import UUID

import structlog
from opentelemetry import trace
from pydantic import BaseModel
from teampass.domain_core import DomainMethod
from teampass.report.dto import ReportContent
from teampass.report.dto.blocks.image import ImageData
from teampass.report.storage import ReportDAO

from .exceptions import ReportNotFoundException

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class UpdateReportCommand(BaseModel):
    report_id: UUID
    content: ReportContent


class UpdateReportMethod(DomainMethod[UpdateReportCommand, None]):
    def __init__(
        self,
        report_dao: ReportDAO,
    ) -> None:
        self.report_dao: ReportDAO = report_dao

    @override
    async def __call__(self, command: UpdateReportCommand) -> None:
        with _tracer.start_as_current_span("report.update") as span:
            span.set_attribute("report.id", str(command.report_id))
            logger = _logger.bind(report_id=str(command.report_id))

            logger.info("updating_report")

            report = await self.report_dao.find_by_id(command.report_id)
            if report is None:
                logger.error("report_not_found")
                raise ReportNotFoundException(command.report_id)

            for block in command.content.blocks:
                if isinstance(block.data, ImageData):
                    block.data.clean_url()

            report.content = command.content.model_dump(mode="json")
            await self.report_dao.save(report)
            await self.report_dao.commit()

            logger.info("report_updated")
