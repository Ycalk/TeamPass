from dishka import Provider, Scope, provide, provide_all
from dishka.dependency_source import CompositeDependencySource
from sqlalchemy.ext.asyncio import AsyncSession

from .methods import (
    CompleteDealMethod,
    CreateDealMethod,
    CreateDealReportMethod,
    CreateListingMethod,
    CreateResponseMethod,
    UpdateDealReportMethod,
)
from .policies import MarketPolicies
from .storage import (
    MarketDealDAO,
    MarketDealDAOFactory,
    MarketListingDAO,
    MarketListingDAOFactory,
    MarketResponseDAO,
    MarketResponseDAOFactory,
)


class MarketProvider(Provider):
    methods: CompositeDependencySource = provide_all(
        CompleteDealMethod,
        CreateListingMethod,
        CreateResponseMethod,
        CreateDealMethod,
        CreateDealReportMethod,
        UpdateDealReportMethod,
        scope=Scope.REQUEST,
    )

    data_access_objects: CompositeDependencySource = provide_all(
        MarketListingDAO,
        MarketResponseDAO,
        MarketDealDAO,
        scope=Scope.REQUEST,
    )

    data_access_object_factories: CompositeDependencySource = provide_all(
        MarketListingDAOFactory,
        MarketResponseDAOFactory,
        MarketDealDAOFactory,
        scope=Scope.REQUEST,
    )

    @provide(scope=Scope.REQUEST)
    async def policies(self, session: AsyncSession) -> MarketPolicies:
        return await MarketPolicies(session).sync()
