from collections.abc import AsyncIterator

import pytest_asyncio
from dishka import AsyncContainer, Provider, make_async_container
from teampass.database import DatabaseProvider
from teampass.team import TeamProvider
from teampass.team.methods import (
    AcceptInvitationMethod,
    CreateTeamMethod,
    DeleteInvitationMethod,
    InviteToTeamMethod,
    LeaveTeamMethod,
    RemoveTeamMemberMethod,
    RenameTeamMethod,
    TransferCaptaincyMethod,
)
from teampass.team.policies import TeamPolicies
from teampass.team.storage import TeamDAO, TeamInvitationDAO
from teampass.user import UserProvider
from teampass.user.storage import StudentDAO, UserDAO


@pytest_asyncio.fixture(scope="class")
async def app_container(
    test_database_provider: Provider,
) -> AsyncIterator[AsyncContainer]:
    container = make_async_container(
        DatabaseProvider(), test_database_provider, UserProvider(), TeamProvider()
    )
    yield container
    await container.close()


@pytest_asyncio.fixture
async def user_dao(request_container: AsyncContainer) -> UserDAO:
    return await request_container.get(UserDAO)


@pytest_asyncio.fixture
async def student_dao(request_container: AsyncContainer) -> StudentDAO:
    return await request_container.get(StudentDAO)


@pytest_asyncio.fixture
async def team_dao(request_container: AsyncContainer) -> TeamDAO:
    return await request_container.get(TeamDAO)


@pytest_asyncio.fixture
async def invitation_dao(request_container: AsyncContainer) -> TeamInvitationDAO:
    return await request_container.get(TeamInvitationDAO)


@pytest_asyncio.fixture
async def create_team_method(request_container: AsyncContainer) -> CreateTeamMethod:
    return await request_container.get(CreateTeamMethod)


@pytest_asyncio.fixture
async def invite_to_team_method(
    request_container: AsyncContainer,
) -> InviteToTeamMethod:
    return await request_container.get(InviteToTeamMethod)


@pytest_asyncio.fixture
async def accept_invitation_method(
    request_container: AsyncContainer,
) -> AcceptInvitationMethod:
    return await request_container.get(AcceptInvitationMethod)


@pytest_asyncio.fixture
async def delete_invitation_method(
    request_container: AsyncContainer,
) -> DeleteInvitationMethod:
    return await request_container.get(DeleteInvitationMethod)


@pytest_asyncio.fixture
async def remove_team_member_method(
    request_container: AsyncContainer,
) -> RemoveTeamMemberMethod:
    return await request_container.get(RemoveTeamMemberMethod)


@pytest_asyncio.fixture
async def leave_team_method(request_container: AsyncContainer) -> LeaveTeamMethod:
    return await request_container.get(LeaveTeamMethod)


@pytest_asyncio.fixture
async def transfer_captaincy_method(
    request_container: AsyncContainer,
) -> TransferCaptaincyMethod:
    return await request_container.get(TransferCaptaincyMethod)


@pytest_asyncio.fixture
async def rename_team_method(request_container: AsyncContainer) -> RenameTeamMethod:
    return await request_container.get(RenameTeamMethod)


@pytest_asyncio.fixture
async def policies(request_container: AsyncContainer) -> TeamPolicies:
    return await request_container.get(TeamPolicies)
