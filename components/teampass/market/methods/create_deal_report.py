from typing import Final, override
from uuid import UUID

import structlog
from opentelemetry import trace
from pydantic import BaseModel
from teampass.domain_core import DomainMethod
from teampass.market.dto import MarketDeal
from teampass.market.storage import MarketDealDAO, MarketDealLoadEnum, MarketResponseDAO
from teampass.report.dto import ReportContent
from teampass.report.methods import CreateReportCommand, CreateReportMethod
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import UserDAO

from .exceptions import (
    MarketDealNotFoundException,
    ReportAlreadyExistsException,
    ReportUpdateForbiddenException,
    UserNotInTeamException,
)

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class CreateDealReportPayload(BaseModel):
    deal_id: UUID
    content: ReportContent


class CreateDealReportCommand(CreateDealReportPayload):
    user_id: UUID


class CreateDealReportMethod(DomainMethod[CreateDealReportCommand, MarketDeal]):
    def __init__(
        self,
        market_deal_dao: MarketDealDAO,
        market_response_dao: MarketResponseDAO,
        user_dao: UserDAO,
        create_report: CreateReportMethod,
    ) -> None:
        self.market_deal_dao: MarketDealDAO = market_deal_dao
        self.market_response_dao: MarketResponseDAO = market_response_dao
        self.user_dao: UserDAO = user_dao
        self.create_report: CreateReportMethod = create_report

    @override
    async def __call__(self, command: CreateDealReportCommand) -> MarketDeal:
        with _tracer.start_as_current_span("market.create_deal_report") as span:
            span.set_attribute("user.id", str(command.user_id))
            span.set_attribute("deal.id", str(command.deal_id))
            logger = _logger.bind(
                user_id=str(command.user_id),
                deal_id=str(command.deal_id),
            )

            logger.info("creating_deal_report")

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

            # Only the responding team can create the report
            if deal.market_response.team_id != user.team_id:
                logger.error(
                    "report_creation_forbidden",
                    response_team_id=str(deal.market_response.team_id),
                    user_team_id=str(user.team_id),
                )
                raise ReportUpdateForbiddenException(command.user_id, command.deal_id)

            if deal.report_id is not None:
                logger.error("report_already_exists", report_id=str(deal.report_id))
                raise ReportAlreadyExistsException(command.deal_id)

            report_id = await self.create_report(
                CreateReportCommand(
                    user_id=command.user_id,
                    content=command.content,
                )
            )
            deal.report_id = report_id
            await self.market_deal_dao.save(deal)
            await self.market_deal_dao.commit()

            span.set_attribute("report.id", str(report_id))
            logger.info("deal_report_created", report_id=str(report_id))

            return MarketDeal.from_persistent(deal)
