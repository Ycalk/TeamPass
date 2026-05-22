import pytest
from dishka.entities.depends_marker import FromDishka
from teampass.market.methods import (
    CreateDealCommand,
    CreateDealMethod,
    CreateDealReportCommand,
    CreateDealReportMethod,
    CreateListingCommand,
    CreateListingMethod,
    CreateResponseCommand,
    CreateResponseMethod,
    ReportUpdateForbiddenException,
)
from teampass.market.storage import MarketDealDAO
from teampass.report import ReportContent

from development.pytest_inject import inject

from .conftest import UtilsForTesting


def _make_content() -> ReportContent:
    return ReportContent.model_validate(
        {
            "time": 1000,
            "blocks": [{"id": "p1", "type": "paragraph", "data": {"text": "hello"}}],
            "version": "2.30.6",
        }
    )


@pytest.mark.asyncio
class TestCreateDealReportMethod:
    @inject
    async def test_success(
        self,
        create_listing_method: FromDishka[CreateListingMethod],
        create_response_method: FromDishka[CreateResponseMethod],
        create_deal_method: FromDishka[CreateDealMethod],
        create_deal_report_method: FromDishka[CreateDealReportMethod],
        market_deal_dao: FromDishka[MarketDealDAO],
        factory: UtilsForTesting,
    ) -> None:
        team1 = await factory.create_team("TR1")
        user1 = await factory.create_user("ur1@t.com", "ur1", team1.id)
        team2 = await factory.create_team("TR2")
        user2 = await factory.create_user("ur2@t.com", "ur2", team2.id)
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

        await create_deal_report_method(
            CreateDealReportCommand(
                user_id=user2.id, deal_id=deal.id, content=_make_content()
            )
        )
        deal_obj = await market_deal_dao.find_by_id(deal.id)

        assert deal_obj is not None
        assert deal_obj.report_id is not None

    @inject
    async def test_report_creation_forbidden(
        self,
        create_listing_method: FromDishka[CreateListingMethod],
        create_response_method: FromDishka[CreateResponseMethod],
        create_deal_method: FromDishka[CreateDealMethod],
        create_deal_report_method: FromDishka[CreateDealReportMethod],
        factory: UtilsForTesting,
    ) -> None:
        team1 = await factory.create_team("TR3")
        user1 = await factory.create_user("ur3@t.com", "ur3", team1.id)
        team2 = await factory.create_team("TR4")
        user2 = await factory.create_user("ur4@t.com", "ur4", team2.id)
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

        # Lister tries to create report
        with pytest.raises(ReportUpdateForbiddenException):
            await create_deal_report_method(
                CreateDealReportCommand(
                    user_id=user1.id, deal_id=deal.id, content=_make_content()
                )
            )
