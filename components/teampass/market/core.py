from dishka import Provider, Scope, provide_all
from dishka.dependency_source import CompositeDependencySource

from .storage import (
    MarketDealDAO,
    MarketDealDAOFactory,
    MarketListingDAO,
    MarketListingDAOFactory,
    MarketResponseDAO,
    MarketResponseDAOFactory,
)


class MarketProvider(Provider):
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
