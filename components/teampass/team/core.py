from dishka import Provider, Scope, provide_all
from dishka.dependency_source import CompositeDependencySource

from .storage import TeamDAO


class TeamProvider(Provider):
    data_access_objects: CompositeDependencySource = provide_all(
        TeamDAO,
        scope=Scope.REQUEST,
    )
