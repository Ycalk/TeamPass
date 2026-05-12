from typing import Final, override
from uuid import UUID

import structlog
from opentelemetry import trace
from pydantic import BaseModel
from teampass.domain_core import DomainMethod
from teampass.report.dto import ReportContent
from teampass.report.storage import ReportDAO
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import UserDAO

from .update_report import UpdateReportCommand, UpdateReportMethod

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class CreateReportCommand(BaseModel):
    user_id: UUID
    content: ReportContent


class CreateReportMethod(DomainMethod[CreateReportCommand, UUID]):
    def __init__(
        self,
        report_dao: ReportDAO,
        user_dao: UserDAO,
        update_report: UpdateReportMethod,
    ) -> None:
        self.report_dao: ReportDAO = report_dao
        self.user_dao: UserDAO = user_dao
        self.update_report: UpdateReportMethod = update_report

    @override
    async def __call__(self, command: CreateReportCommand) -> UUID:
        with _tracer.start_as_current_span("report.create") as span:
            span.set_attribute("user.id", str(command.user_id))
            logger = _logger.bind(user_id=str(command.user_id))

            logger.info("creating_report")

            user = await self.user_dao.find_by_id(command.user_id)
            if user is None:
                logger.error("user_not_found")
                raise UserNotFoundException(command.user_id)

            report = await self.report_dao.create(
                content={},
                owner_id=command.user_id,
            )
            await self.update_report(
                UpdateReportCommand(report_id=report.id, content=command.content)
            )
            await self.report_dao.commit()

            span.set_attribute("report.id", str(report.id))
            logger.info("report_created", report_id=str(report.id))

            return report.id
