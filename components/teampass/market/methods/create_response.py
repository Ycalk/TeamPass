from typing import Final, override
from uuid import UUID

import structlog
from opentelemetry import trace
from pydantic import BaseModel
from teampass.domain_core import DomainMethod
from teampass.market.dto import MarketResponse
from teampass.market.storage import (
    MarketListingDAO,
    MarketListingLoadEnum,
    MarketResponseDAO,
    MarketResponseLoadEnum,
    MarketResponseStatus,
)
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import UserDAO

from .exceptions import (
    ListingClosedException,
    MarketListingNotFoundException,
    UserNotInTeamException,
)

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class CreateResponsePayload(BaseModel):
    market_listing_id: UUID


class CreateResponseCommand(CreateResponsePayload):
    user_id: UUID


class CreateResponseMethod(DomainMethod[CreateResponseCommand, MarketResponse]):
    def __init__(
        self,
        market_response_dao: MarketResponseDAO,
        market_listing_dao: MarketListingDAO,
        user_dao: UserDAO,
    ) -> None:
        self.market_response_dao: MarketResponseDAO = market_response_dao
        self.market_listing_dao: MarketListingDAO = market_listing_dao
        self.user_dao: UserDAO = user_dao

    @override
    async def __call__(self, command: CreateResponseCommand) -> MarketResponse:
        with _tracer.start_as_current_span("market.create_response") as span:
            span.set_attribute("user.id", str(command.user_id))
            span.set_attribute("listing.id", str(command.market_listing_id))
            logger = _logger.bind(
                user_id=str(command.user_id),
                listing_id=str(command.market_listing_id),
            )

            logger.info("creating_market_response")

            user = await self.user_dao.find_by_id(command.user_id)
            if user is None:
                logger.error("user_not_found")
                raise UserNotFoundException(command.user_id)

            if user.team_id is None:
                logger.error("user_has_no_team")
                raise UserNotInTeamException(command.user_id)

            listing = await self.market_listing_dao.find_by_id(
                command.market_listing_id,
                includes=[MarketListingLoadEnum.MARKET_RESPONSES],
            )
            if listing is None:
                logger.error("listing_not_found")
                raise MarketListingNotFoundException(command.market_listing_id)

            if any(
                market_response.status == MarketResponseStatus.ACCEPTED
                for market_response in listing.market_responses
            ):
                raise ListingClosedException(listing.id)

            response = await self.market_response_dao.create(
                responder_id=command.user_id,
                team_id=user.team_id,
                market_listing_id=command.market_listing_id,
            )
            await self.market_response_dao.commit()

            span.set_attribute("response.id", str(response.id))
            logger.info("market_response_created", response_id=str(response.id))

            response = await self.market_response_dao.find_by_id(
                response.id, includes=[MarketResponseLoadEnum.TEAM]
            )
            if response is None:
                raise ValueError("Unexpected error: response not found")

            return MarketResponse.from_persistent(response)
