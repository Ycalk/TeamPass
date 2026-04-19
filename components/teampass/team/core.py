from dishka import Provider, Scope, provide_all
from dishka.dependency_source import CompositeDependencySource

from .methods import (
    AcceptInvitationMethod,
    CreateTeamMethod,
    DeleteInvitationMethod,
    InviteToTeamMethod,
    LeaveTeamMethod,
    RemoveTeamMemberMethod,
    RenameTeamMethod,
    TransferCaptaincyMethod,
)
from .storage import (
    TeamDAO,
    TeamDAOFactory,
    TeamInvitationDAO,
    TeamInvitationDAOFactory,
)


class TeamProvider(Provider):
    methods: CompositeDependencySource = provide_all(
        AcceptInvitationMethod,
        CreateTeamMethod,
        DeleteInvitationMethod,
        InviteToTeamMethod,
        LeaveTeamMethod,
        RemoveTeamMemberMethod,
        RenameTeamMethod,
        TransferCaptaincyMethod,
        scope=Scope.REQUEST,
    )

    data_access_objects: CompositeDependencySource = provide_all(
        TeamDAO,
        TeamInvitationDAO,
        scope=Scope.REQUEST,
    )

    data_access_object_factories: CompositeDependencySource = provide_all(
        TeamDAOFactory,
        TeamInvitationDAOFactory,
        scope=Scope.REQUEST,
    )
