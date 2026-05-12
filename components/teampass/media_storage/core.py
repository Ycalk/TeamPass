from dishka import Provider, Scope, provide, provide_all
from dishka.dependency_source import CompositeDependencySource

from .methods import GetMediaMethod, SaveMediaMethod
from .s3.client import IS3Client, S3Client
from .settings import MediaStorageSettings
from .storage import MediaDAO, MediaDAOFactory


class MediaStorageProvider(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> MediaStorageSettings:
        return MediaStorageSettings()  # type: ignore # pyright: ignore

    s3_client: CompositeDependencySource = provide(
        S3Client, scope=Scope.APP, provides=IS3Client
    )

    methods: CompositeDependencySource = provide_all(
        GetMediaMethod,
        SaveMediaMethod,
        scope=Scope.REQUEST,
    )

    media_dao: CompositeDependencySource = provide(
        MediaDAO,
        scope=Scope.REQUEST,
    )

    media_dao_factory: CompositeDependencySource = provide(
        MediaDAOFactory,
        scope=Scope.REQUEST,
    )
