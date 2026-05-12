from dishka import Provider, Scope, provide, provide_all
from dishka.dependency_source import CompositeDependencySource
from sqlalchemy.ext.asyncio import AsyncSession

from .methods import (
    CreateCycleMethod,
    CreateSnapshotMethod,
    CreateTransactionMethod,
    GetCurrentCycleMethod,
)
from .policies import TransactionPolicies
from .storage import (
    CycleSnapshotDAO,
    CycleSnapshotDAOFactory,
    GameCycleDAO,
    GameCycleDAOFactory,
    PointTransactionDAO,
    PointTransactionDAOFactory,
)


class TransactionProvider(Provider):
    methods: CompositeDependencySource = provide_all(
        CreateCycleMethod,
        CreateSnapshotMethod,
        CreateTransactionMethod,
        GetCurrentCycleMethod,
        scope=Scope.REQUEST,
    )

    data_access_objects: CompositeDependencySource = provide_all(
        CycleSnapshotDAO,
        GameCycleDAO,
        PointTransactionDAO,
        scope=Scope.REQUEST,
    )

    data_access_object_factories: CompositeDependencySource = provide_all(
        CycleSnapshotDAOFactory,
        GameCycleDAOFactory,
        PointTransactionDAOFactory,
        scope=Scope.REQUEST,
    )

    @provide(scope=Scope.REQUEST)
    async def policies(self, session: AsyncSession) -> TransactionPolicies:
        return await TransactionPolicies(session).sync()
