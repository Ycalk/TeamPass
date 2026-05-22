import pytest
from dishka.entities.depends_marker import FromDishka
from teampass.market.methods import (
    CompleteDealCommand,
    CompleteDealMethod,
    CreateDealCommand,
    CreateDealMethod,
    CreateListingCommand,
    CreateListingMethod,
    CreateResponseCommand,
    CreateResponseMethod,
    DealCompletionForbiddenException,
)
from teampass.market.storage import MarketDealDAO, MarketDealStatus
from teampass.transaction.storage import PointTransactionDAO, PointType

from development.pytest_inject import inject

from .conftest import UtilsForTesting


@pytest.mark.asyncio
class TestCompleteDealMethod:
    @inject
    async def test_success(
        self,
        create_listing_method: FromDishka[CreateListingMethod],
        create_response_method: FromDishka[CreateResponseMethod],
        create_deal_method: FromDishka[CreateDealMethod],
        complete_deal_method: FromDishka[CompleteDealMethod],
        market_deal_dao: FromDishka[MarketDealDAO],
        point_transaction_dao: FromDishka[PointTransactionDAO],
        factory: UtilsForTesting,
    ) -> None:
        team1 = await factory.create_team("TC1")
        user1 = await factory.create_user("uc1@t.com", "uc1", team1.id)
        team2 = await factory.create_team("TC2")
        user2 = await factory.create_user("uc2@t.com", "uc2", team2.id)
        cycle = await factory.create_game_cycle()

        listing = await create_listing_method(
            CreateListingCommand(user_id=user1.id, title="T", description="D")
        )
        resp = await create_response_method(
            CreateResponseCommand(user_id=user2.id, market_listing_id=listing.id)
        )
        deal = await create_deal_method(
            CreateDealCommand(user_id=user1.id, response_id=resp.id)
        )

        completed_deal = await complete_deal_method(
            CompleteDealCommand(user_id=user2.id, deal_id=deal.id)
        )

        db_deal = await market_deal_dao.find_by_id(completed_deal.id)
        assert db_deal and db_deal.status == MarketDealStatus.COMPLETED

        # Check that transaction was created for responder team
        transactions = await point_transaction_dao.sum_points_by_type(
            cycle_id=cycle.id, team_id=team2.id
        )
        assert transactions.get(PointType.ACTIVITY, 0) == 40

    @inject
    async def test_deal_completion_forbidden(
        self,
        create_listing_method: FromDishka[CreateListingMethod],
        create_response_method: FromDishka[CreateResponseMethod],
        create_deal_method: FromDishka[CreateDealMethod],
        complete_deal_method: FromDishka[CompleteDealMethod],
        factory: UtilsForTesting,
    ) -> None:
        team1 = await factory.create_team("TC3")
        user1 = await factory.create_user("uc3@t.com", "uc3", team1.id)
        team2 = await factory.create_team("TC4")
        user2 = await factory.create_user("uc4@t.com", "uc4", team2.id)
        await factory.create_game_cycle()

        listing = await create_listing_method(
            CreateListingCommand(user_id=user1.id, title="T", description="D")
        )
        resp = await create_response_method(
            CreateResponseCommand(user_id=user2.id, market_listing_id=listing.id)
        )
        deal = await create_deal_method(
            CreateDealCommand(user_id=user1.id, response_id=resp.id)
        )

        # Lister tries to complete deal
        with pytest.raises(DealCompletionForbiddenException):
            await complete_deal_method(
                CompleteDealCommand(user_id=user1.id, deal_id=deal.id)
            )
