from typing import Final, override
from uuid import UUID

import structlog
from opentelemetry import trace
from pydantic import BaseModel
from teampass.domain_core import DomainMethod
from teampass.market.dto import MarketListing
from teampass.market.policies import MarketPolicies
from teampass.market.storage import MarketListingDAO, MarketListingLoadEnum
from teampass.transaction.methods import GetCurrentCycleMethod
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import UserDAO

from .exceptions import (
    ListingsLimitReachedException,
    NoActiveGameCycleException,
    UserNotInTeamException,
)

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class CreateListingPayload(BaseModel):
    title: str
    description: str


class CreateListingCommand(CreateListingPayload):
    user_id: UUID


class CreateListingMethod(DomainMethod[CreateListingCommand, MarketListing]):
    def __init__(
        self,
        market_listing_dao: MarketListingDAO,
        user_dao: UserDAO,
        get_current_cycle: GetCurrentCycleMethod,
        policies: MarketPolicies,
    ) -> None:
        self.market_listing_dao: MarketListingDAO = market_listing_dao
        self.user_dao: UserDAO = user_dao
        self.get_current_cycle: GetCurrentCycleMethod = get_current_cycle
        self.policies: MarketPolicies = policies

    @override
    async def __call__(self, command: CreateListingCommand) -> MarketListing:
        with _tracer.start_as_current_span("market.create_listing") as span:
            span.set_attribute("user.id", str(command.user_id))
            logger = _logger.bind(user_id=str(command.user_id))

            logger.info("creating_market_listing")

            user = await self.user_dao.find_by_id(command.user_id)
            if user is None:
                logger.error("user_not_found")
                raise UserNotFoundException(command.user_id)

            if user.team_id is None:
                logger.error("user_has_no_team")
                raise UserNotInTeamException(command.user_id)

            cycle = await self.get_current_cycle(None)
            if cycle is None:
                logger.error("no_active_game_cycle")
                raise NoActiveGameCycleException()

            span.set_attribute("cycle.id", str(cycle.id))
            span.set_attribute("team.id", str(user.team_id))

            current_count = await self.market_listing_dao.count_by_team_and_cycle(
                team_id=user.team_id,
                game_cycle_id=cycle.id,
            )
            if current_count >= self.policies.listings_limit:
                logger.error(
                    "listings_limit_reached",
                    team_id=str(user.team_id),
                    limit=self.policies.listings_limit,
                    current_count=current_count,
                )
                raise ListingsLimitReachedException(
                    user.team_id, self.policies.listings_limit
                )

            listing = await self.market_listing_dao.create(
                title=command.title,
                description=command.description,
                team_id=user.team_id,
                game_cycle_id=cycle.id,
                author_id=command.user_id,
            )
            await self.market_listing_dao.commit()

            span.set_attribute("listing.id", str(listing.id))
            logger.info("market_listing_created", listing_id=str(listing.id))

            listing = await self.market_listing_dao.find_by_id(
                listing.id, includes=[MarketListingLoadEnum.TEAM]
            )
            if listing is None:
                raise ValueError("Unexpected error: listing not found")

            return MarketListing.from_persistent(listing)
