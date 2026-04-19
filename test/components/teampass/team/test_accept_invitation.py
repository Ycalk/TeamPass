from uuid import uuid4

import pytest
from teampass.team.methods import (
    AcceptInvitationCommand,
    AcceptInvitationMethod,
    CreateTeamCommand,
    CreateTeamMethod,
    InviteToTeamCommand,
    InviteToTeamMethod,
)
from teampass.team.methods.exceptions import (
    InvitationNotFoundException,
    UserAlreadyInTeamException,
)
from teampass.user.storage import StudentDAO, UserDAO


@pytest.mark.asyncio
class TestAcceptInvitationMethod:
    async def test_accept_invitation_success(
        self,
        create_team_method: CreateTeamMethod,
        invite_to_team_method: InviteToTeamMethod,
        accept_invitation_method: AcceptInvitationMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        # Inviter setup
        student_inviter = await student_dao.create(
            student_id="tai_success_inviter",
            first_name="A",
            last_name="B",
            patronymic=None,
        )
        inviter = await user_dao.create(
            email="tai_success_inviter@example.com",
            password_hash="hash",
            student_id=student_inviter.id,
        )
        await create_team_method(CreateTeamCommand(name="Team A", user_id=inviter.id))

        # Invited setup
        student_invited = await student_dao.create(
            student_id="tai_success_invited",
            first_name="C",
            last_name="D",
            patronymic=None,
        )
        invited = await user_dao.create(
            email="tai_success_invited@example.com",
            password_hash="hash",
            student_id=student_invited.id,
        )

        invitation = await invite_to_team_method(
            InviteToTeamCommand(user_id=inviter.id, invited_user_id=invited.id)
        )

        command = AcceptInvitationCommand(
            invitation_id=invitation.id, user_id=invited.id
        )
        accepted_dto = await accept_invitation_method(command)

        assert accepted_dto is not None
        assert accepted_dto.accepted_at is not None

        invited_refreshed = await user_dao.find_by_id(invited.id)
        assert invited_refreshed is not None
        assert invited_refreshed.team_id == accepted_dto.team.id

    async def test_accept_invitation_not_found(
        self,
        accept_invitation_method: AcceptInvitationMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        student = await student_dao.create(
            student_id="tai_not_found", first_name="A", last_name="B", patronymic=None
        )
        user = await user_dao.create(
            email="tai_not_found@example.com",
            password_hash="hash",
            student_id=student.id,
        )

        fake_id = uuid4()
        command = AcceptInvitationCommand(invitation_id=fake_id, user_id=user.id)

        with pytest.raises(InvitationNotFoundException) as exc_info:
            await accept_invitation_method(command)
        assert exc_info.value.invitation_id == fake_id

    async def test_accept_someone_elses_invitation(
        self,
        create_team_method: CreateTeamMethod,
        invite_to_team_method: InviteToTeamMethod,
        accept_invitation_method: AcceptInvitationMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        # Inviter
        student_inviter = await student_dao.create(
            student_id="tai_wrong_inviter",
            first_name="A",
            last_name="B",
            patronymic=None,
        )
        inviter = await user_dao.create(
            email="tai_wrong_inviter@example.com",
            password_hash="hash",
            student_id=student_inviter.id,
        )
        await create_team_method(CreateTeamCommand(name="Team A", user_id=inviter.id))

        # Invited
        student_invited = await student_dao.create(
            student_id="tai_wrong_invited",
            first_name="C",
            last_name="D",
            patronymic=None,
        )
        invited = await user_dao.create(
            email="tai_wrong_invited@example.com",
            password_hash="hash",
            student_id=student_invited.id,
        )

        # Sneaky outsider
        student_sneaky = await student_dao.create(
            student_id="tai_sneaky", first_name="E", last_name="F", patronymic=None
        )
        sneaky = await user_dao.create(
            email="tai_sneaky@example.com",
            password_hash="hash",
            student_id=student_sneaky.id,
        )

        invitation = await invite_to_team_method(
            InviteToTeamCommand(user_id=inviter.id, invited_user_id=invited.id)
        )

        command = AcceptInvitationCommand(
            invitation_id=invitation.id, user_id=sneaky.id
        )
        with pytest.raises(InvitationNotFoundException):
            await accept_invitation_method(command)

    async def test_accept_invitation_already_in_team(
        self,
        create_team_method: CreateTeamMethod,
        invite_to_team_method: InviteToTeamMethod,
        accept_invitation_method: AcceptInvitationMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        # Inviter
        student_inviter = await student_dao.create(
            student_id="tai_already_inviter",
            first_name="A",
            last_name="B",
            patronymic=None,
        )
        inviter = await user_dao.create(
            email="tai_already_inviter@example.com",
            password_hash="hash",
            student_id=student_inviter.id,
        )
        await create_team_method(CreateTeamCommand(name="Team A", user_id=inviter.id))

        # Invited
        student_invited = await student_dao.create(
            student_id="tai_already_invited",
            first_name="C",
            last_name="D",
            patronymic=None,
        )
        invited = await user_dao.create(
            email="tai_already_invited@example.com",
            password_hash="hash",
            student_id=student_invited.id,
        )

        invitation = await invite_to_team_method(
            InviteToTeamCommand(user_id=inviter.id, invited_user_id=invited.id)
        )

        # Invited user somehow joins another team before accepting
        await create_team_method(CreateTeamCommand(name="Team B", user_id=invited.id))

        command = AcceptInvitationCommand(
            invitation_id=invitation.id, user_id=invited.id
        )
        with pytest.raises(UserAlreadyInTeamException):
            await accept_invitation_method(command)
