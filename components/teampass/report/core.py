from dishka import Provider, Scope, provide_all
from dishka.dependency_source import CompositeDependencySource

from .methods import (
    CreateReportMethod,
    GetReportMethod,
    UpdateReportMethod,
    UploadMediaMethod,
)
from .storage import ReportDAO, ReportDAOFactory


class ReportProvider(Provider):
    methods: CompositeDependencySource = provide_all(
        CreateReportMethod,
        GetReportMethod,
        UpdateReportMethod,
        UploadMediaMethod,
        scope=Scope.REQUEST,
    )

    data_access_object: CompositeDependencySource = provide_all(
        ReportDAO,
        scope=Scope.REQUEST,
    )

    data_access_object_factory: CompositeDependencySource = provide_all(
        ReportDAOFactory,
        scope=Scope.REQUEST,
    )
