from typing import Final, override
from uuid import UUID

import structlog
from opentelemetry import trace
from pydantic import BaseModel
from teampass.domain_core import DomainMethod
from teampass.market.dto import MarketDeal
from teampass.market.storage import (
    MarketDealDAO,
    MarketResponseDAO,
    MarketResponseLoadEnum,
    MarketResponseStatus,
)
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import UserDAO

from .exceptions import (
    DealCreationForbiddenException,
    MarketResponseNotFoundException,
    UserNotInTeamException,
)

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class CreateDealPayload(BaseModel):
    response_id: UUID


class CreateDealCommand(CreateDealPayload):
    user_id: UUID


class CreateDealMethod(DomainMethod[CreateDealCommand, MarketDeal]):
    def __init__(
        self,
        market_deal_dao: MarketDealDAO,
        market_response_dao: MarketResponseDAO,
        user_dao: UserDAO,
    ) -> None:
        self.market_deal_dao: MarketDealDAO = market_deal_dao
        self.market_response_dao: MarketResponseDAO = market_response_dao
        self.user_dao: UserDAO = user_dao

    @override
    async def __call__(self, command: CreateDealCommand) -> MarketDeal:
        with _tracer.start_as_current_span("market.create_deal") as span:
            span.set_attribute("user.id", str(command.user_id))
            span.set_attribute("response.id", str(command.response_id))
            logger = _logger.bind(
                user_id=str(command.user_id),
                response_id=str(command.response_id),
            )

            logger.info("creating_market_deal")

            user = await self.user_dao.find_by_id(command.user_id)
            if user is None:
                logger.error("user_not_found")
                raise UserNotFoundException(command.user_id)

            if user.team_id is None:
                logger.error("user_has_no_team")
                raise UserNotInTeamException(command.user_id)

            response = await self.market_response_dao.find_by_id(
                command.response_id, includes=[MarketResponseLoadEnum.MARKET_LISTING]
            )
            if response is None:
                logger.error("response_not_found")
                raise MarketResponseNotFoundException(command.response_id)

            # Only the team that created the listing can accept a response
            if response.market_listing.team_id != user.team_id:
                logger.error(
                    "deal_creation_forbidden",
                    listing_team_id=str(response.market_listing.team_id),
                    user_team_id=str(user.team_id),
                )
                raise DealCreationForbiddenException(
                    command.user_id, response.market_listing.id
                )

            span.set_attribute("listing.id", str(response.market_listing.id))

            # Accept the chosen response
            response.status = MarketResponseStatus.ACCEPTED
            await self.market_response_dao.save(response)

            # Reject all other responses for this listing
            await self.market_response_dao.reject_others_for_listing(
                market_listing_id=response.market_listing.id,
                accepted_response_id=response.id,
            )

            deal = await self.market_deal_dao.create(
                market_response_id=response.id,
            )
            await self.market_deal_dao.commit()

            span.set_attribute("deal.id", str(deal.id))
            logger.info("market_deal_created", deal_id=str(deal.id))

            return MarketDeal.from_persistent(deal)
