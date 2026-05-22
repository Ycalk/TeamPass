from uuid import uuid4

import pytest
from dishka.entities.depends_marker import FromDishka
from teampass.market import MarketResponse
from teampass.market.methods import (
    CreateListingCommand,
    CreateListingMethod,
    CreateResponseCommand,
    CreateResponseMethod,
    MarketListingNotFoundException,
)
from teampass.market.storage import MarketResponseDAO, MarketResponseStatus

from development.pytest_inject import inject

from .conftest import UtilsForTesting


@pytest.mark.asyncio
class TestCreateResponseMethod:
    @inject
    async def test_success(
        self,
        create_listing_method: FromDishka[CreateListingMethod],
        create_response_method: FromDishka[CreateResponseMethod],
        market_response_dao: FromDishka[MarketResponseDAO],
        factory: UtilsForTesting,
    ) -> None:
        team1 = await factory.create_team("Listers")
        user1 = await factory.create_user("lister@test.com", "lister", team1.id)
        team2 = await factory.create_team("Responders")
        user2 = await factory.create_user("responder@test.com", "responder", team2.id)
        await factory.create_game_cycle()

        listing = await create_listing_method(
            CreateListingCommand(user_id=user1.id, title="Task", description="Desc")
        )

        response = await create_response_method(
            CreateResponseCommand(user_id=user2.id, market_listing_id=listing.id)
        )

        assert isinstance(response, MarketResponse)
        assert response.market_listing_id == listing.id
        assert response.team.id == team2.id
        assert response.status == MarketResponseStatus.PENDING

        db_resp = await market_response_dao.find_by_id(response.id)
        assert db_resp is not None
        assert db_resp.responder_id == user2.id

    @inject
    async def test_listing_not_found(
        self,
        create_response_method: FromDishka[CreateResponseMethod],
        factory: UtilsForTesting,
    ) -> None:
        team = await factory.create_team("T")
        user = await factory.create_user("u@t.com", "ut", team.id)
        with pytest.raises(MarketListingNotFoundException):
            await create_response_method(
                CreateResponseCommand(user_id=user.id, market_listing_id=uuid4())
            )
