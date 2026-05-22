from typing import Final, override
from uuid import UUID

import structlog
from opentelemetry import trace
from pydantic import BaseModel
from teampass.domain_core import DomainMethod
from teampass.market.dto import MarketDeal
from teampass.market.policies import MarketPolicies
from teampass.market.storage import (
    MarketDealDAO,
    MarketDealLoadEnum,
    MarketDealStatus,
    MarketListingDAO,
)
from teampass.transaction.methods import (
    CreateTransactionCommand,
    CreateTransactionMethod,
)
from teampass.transaction.storage import PointType
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import UserDAO

from .exceptions import (
    DealCompletionForbiddenException,
    MarketDealNotFoundException,
    UserNotInTeamException,
)

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class CompleteDealCommand(BaseModel):
    user_id: UUID
    deal_id: UUID


class CompleteDealMethod(DomainMethod[CompleteDealCommand, MarketDeal]):
    def __init__(
        self,
        market_deal_dao: MarketDealDAO,
        market_listing_dao: MarketListingDAO,
        user_dao: UserDAO,
        create_transaction: CreateTransactionMethod,
        policies: MarketPolicies,
    ) -> None:
        self.market_deal_dao: MarketDealDAO = market_deal_dao
        self.market_listing_dao: MarketListingDAO = market_listing_dao
        self.user_dao: UserDAO = user_dao
        self.create_transaction: CreateTransactionMethod = create_transaction
        self.policies: MarketPolicies = policies

    @override
    async def __call__(self, command: CompleteDealCommand) -> MarketDeal:
        with _tracer.start_as_current_span("market.complete_deal") as span:
            span.set_attribute("user.id", str(command.user_id))
            span.set_attribute("deal.id", str(command.deal_id))
            logger = _logger.bind(
                user_id=str(command.user_id),
                deal_id=str(command.deal_id),
            )

            logger.info("completing_market_deal")

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

            # Only the team that created the response can complete the deal
            if deal.market_response.team_id != user.team_id:
                logger.error(
                    "deal_completion_forbidden",
                    response_team_id=str(deal.market_response.team_id),
                    user_team_id=str(user.team_id),
                )
                raise DealCompletionForbiddenException(command.user_id, command.deal_id)

            if deal.status == MarketDealStatus.COMPLETED:
                logger.info("deal_already_completed")
                return MarketDeal.from_persistent(deal)

            deal.status = MarketDealStatus.COMPLETED
            await self.market_deal_dao.save(deal)

            # Reward the responding team
            await self.create_transaction(
                CreateTransactionCommand(
                    team_id=deal.market_response.team_id,
                    points=self.policies.market_points,
                    points_type=PointType.ACTIVITY,
                )
            )

            await self.market_deal_dao.commit()

            span.set_attribute("deal.status", deal.status)
            logger.info(
                "market_deal_completed",
                deal_id=str(deal.id),
                reward_points=self.policies.market_points,
            )

            return MarketDeal.from_persistent(deal)
