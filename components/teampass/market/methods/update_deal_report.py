from typing import Final, override
from uuid import UUID

import structlog
from opentelemetry import trace
from pydantic import BaseModel
from teampass.domain_core import DomainMethod
from teampass.market.dto import MarketDeal
from teampass.market.storage import MarketDealDAO, MarketDealLoadEnum
from teampass.report.dto import ReportContent
from teampass.report.methods import UpdateReportCommand, UpdateReportMethod
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import UserDAO

from .exceptions import (
    MarketDealNotFoundException,
    ReportUpdateForbiddenException,
    UserNotInTeamException,
)

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class UpdateDealReportPayload(BaseModel):
    deal_id: UUID
    content: ReportContent


class UpdateDealReportCommand(UpdateDealReportPayload):
    user_id: UUID


class UpdateDealReportMethod(DomainMethod[UpdateDealReportCommand, MarketDeal]):
    def __init__(
        self,
        market_deal_dao: MarketDealDAO,
        user_dao: UserDAO,
        update_report: UpdateReportMethod,
    ) -> None:
        self.market_deal_dao: MarketDealDAO = market_deal_dao
        self.user_dao: UserDAO = user_dao
        self.update_report: UpdateReportMethod = update_report

    @override
    async def __call__(self, command: UpdateDealReportCommand) -> MarketDeal:
        with _tracer.start_as_current_span("market.update_deal_report") as span:
            span.set_attribute("user.id", str(command.user_id))
            span.set_attribute("deal.id", str(command.deal_id))
            logger = _logger.bind(
                user_id=str(command.user_id),
                deal_id=str(command.deal_id),
            )

            logger.info("updating_deal_report")

            user = await self.user_dao.find_by_id(command.user_id)
            if user is None:
                logger.error("user_not_found")
                raise UserNotFoundException(command.user_id)

            if user.team_id is None:
                logger.error("user_has_no_team")
                raise UserNotInTeamException(command.user_id)

            deal = await self.market_deal_dao.find_by_id(
                command.deal_id, includes=[MarketDealLoadEnum.MARKET_RESPONSE]
            )
            if deal is None:
                logger.error("deal_not_found")
                raise MarketDealNotFoundException(command.deal_id)

            # Only the responding team can update the report
            if deal.market_response.team_id != user.team_id:
                logger.error(
                    "report_update_forbidden",
                    response_team_id=str(deal.market_response.team_id),
                    user_team_id=str(user.team_id),
                )
                raise ReportUpdateForbiddenException(command.user_id, command.deal_id)

            if deal.report_id is None:
                logger.error("report_not_found_for_deal")
                raise MarketDealNotFoundException(command.deal_id)

            await self.update_report(
                UpdateReportCommand(
                    report_id=deal.report_id,
                    content=command.content,
                )
            )

            span.set_attribute("report.id", str(deal.report_id))
            logger.info("deal_report_updated", report_id=str(deal.report_id))

            return MarketDeal.from_persistent(deal)
