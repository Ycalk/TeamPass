import pytest
from dishka.entities.depends_marker import FromDishka
from teampass.market import MarketDeal
from teampass.market.methods import (
    CreateDealCommand,
    CreateDealMethod,
    CreateListingCommand,
    CreateListingMethod,
    CreateResponseCommand,
    CreateResponseMethod,
    DealCreationForbiddenException,
)
from teampass.market.storage import (
    MarketDealDAO,
    MarketDealStatus,
    MarketResponseDAO,
    MarketResponseStatus,
)

from development.pytest_inject import inject

from .conftest import TestFactory


@pytest.mark.asyncio
class TestCreateDealMethod:
    @inject
    async def test_success(
        self,
        create_listing_method: FromDishka[CreateListingMethod],
        create_response_method: FromDishka[CreateResponseMethod],
        create_deal_method: FromDishka[CreateDealMethod],
        market_response_dao: FromDishka[MarketResponseDAO],
        market_deal_dao: FromDishka[MarketDealDAO],
        factory: TestFactory,
    ) -> None:
        team1 = await factory.create_team("T1")
        user1 = await factory.create_user("u1@t.com", "u1", team1.id)
        team2 = await factory.create_team("T2")
        user2 = await factory.create_user("u2@t.com", "u2", team2.id)
        team3 = await factory.create_team("T3")
        user3 = await factory.create_user("u3@t.com", "u3", team3.id)
        await factory.create_game_cycle()

        listing = await create_listing_method(
            CreateListingCommand(user_id=user1.id, title="Task", description="D")
        )
        resp1 = await create_response_method(
            CreateResponseCommand(user_id=user2.id, market_listing_id=listing.id)
        )
        resp2 = await create_response_method(
            CreateResponseCommand(user_id=user3.id, market_listing_id=listing.id)
        )

        deal = await create_deal_method(
            CreateDealCommand(user_id=user1.id, response_id=resp1.id)
        )

        assert isinstance(deal, MarketDeal)
        assert deal.market_response_id == resp1.id

        db_deal = await market_deal_dao.find_by_id(deal.id)
        assert db_deal and db_deal.status == MarketDealStatus.IN_PROGRESS

        # Verify responses status
        r1 = await market_response_dao.find_by_id(resp1.id)
        r2 = await market_response_dao.find_by_id(resp2.id)
        assert r1 and r1.status == MarketResponseStatus.ACCEPTED
        assert r2 and r2.status == MarketResponseStatus.REJECTED

    @inject
    async def test_deal_creation_forbidden(
        self,
        create_listing_method: FromDishka[CreateListingMethod],
        create_response_method: FromDishka[CreateResponseMethod],
        create_deal_method: FromDishka[CreateDealMethod],
        factory: TestFactory,
    ) -> None:
        team1 = await factory.create_team("TF1")
        user1 = await factory.create_user("uf1@t.com", "uf1", team1.id)
        team2 = await factory.create_team("TF2")
        user2 = await factory.create_user("uf2@t.com", "uf2", team2.id)
        await factory.create_game_cycle()

        listing = await create_listing_method(
            CreateListingCommand(user_id=user1.id, title="Task", description="D")
        )
        resp = await create_response_method(
            CreateResponseCommand(user_id=user2.id, market_listing_id=listing.id)
        )

        # user2 cannot accept their own response
        with pytest.raises(DealCreationForbiddenException):
            await create_deal_method(
                CreateDealCommand(user_id=user2.id, response_id=resp.id)
            )
