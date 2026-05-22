from uuid import uuid4

import pytest
from dishka.entities.depends_marker import FromDishka
from teampass.market import MarketListing
from teampass.market.methods import (
    CreateListingCommand,
    CreateListingMethod,
    ListingsLimitReachedException,
    UserNotInTeamException,
)
from teampass.market.storage import MarketListingDAO
from teampass.user.methods import UserNotFoundException

from development.pytest_inject import inject

from .conftest import UtilsForTesting


@pytest.mark.asyncio
class TestCreateListingMethod:
    @inject
    async def test_success(
        self,
        create_listing_method: FromDishka[CreateListingMethod],
        market_listing_dao: FromDishka[MarketListingDAO],
        factory: UtilsForTesting,
    ) -> None:
        team = await factory.create_team("Test Team")
        user = await factory.create_user("l1@test.com", "l1", team.id)
        await factory.create_game_cycle()

        command = CreateListingCommand(
            user_id=user.id, title="Help wanted", description="Need a bugfix"
        )
        listing = await create_listing_method(command)

        assert isinstance(listing, MarketListing)
        assert listing.title == "Help wanted"
        assert listing.team.id == team.id

        db_listing = await market_listing_dao.find_by_id(listing.id)
        assert db_listing is not None
        assert db_listing.author_id == user.id

    @inject
    async def test_user_not_found(
        self, create_listing_method: FromDishka[CreateListingMethod]
    ) -> None:
        command = CreateListingCommand(
            user_id=uuid4(), title="Test", description="Test"
        )
        with pytest.raises(UserNotFoundException):
            await create_listing_method(command)

    @inject
    async def test_user_not_in_team(
        self,
        create_listing_method: FromDishka[CreateListingMethod],
        factory: UtilsForTesting,
    ) -> None:
        user = await factory.create_user("l2@test.com", "l2")
        command = CreateListingCommand(
            user_id=user.id, title="Test", description="Test"
        )
        with pytest.raises(UserNotInTeamException):
            await create_listing_method(command)

    @inject
    async def test_listings_limit_reached(
        self,
        create_listing_method: FromDishka[CreateListingMethod],
        factory: UtilsForTesting,
    ) -> None:
        team = await factory.create_team("Limit Team")
        user = await factory.create_user("limit@test.com", "limit", team.id)
        await factory.create_game_cycle()

        for i in range(3):
            await create_listing_method(
                CreateListingCommand(
                    user_id=user.id, title=f"Task {i}", description="Desc"
                )
            )

        with pytest.raises(ListingsLimitReachedException):
            await create_listing_method(
                CreateListingCommand(
                    user_id=user.id, title="Extra Task", description="Desc"
                )
            )
