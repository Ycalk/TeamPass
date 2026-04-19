from uuid import uuid4

import pytest
from teampass.team.methods import (
    AcceptInvitationCommand,
    AcceptInvitationMethod,
    CreateTeamCommand,
    CreateTeamMethod,
    DeleteInvitationCommand,
    DeleteInvitationMethod,
    InviteToTeamCommand,
    InviteToTeamMethod,
)
from teampass.team.methods.exceptions import (
    InvitationAlreadyAcceptedException,
    InvitationDeleteForbiddenException,
    InvitationNotFoundException,
)
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import StudentDAO, UserDAO


@pytest.mark.asyncio
class TestDeleteInvitationMethod:
    async def test_delete_success_invited_user(
        self,
        create_team_method: CreateTeamMethod,
        invite_to_team_method: InviteToTeamMethod,
        delete_invitation_method: DeleteInvitationMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        # Inviter setup
        student_inviter = await student_dao.create(
            student_id="tdi_succ_u_inviter",
            first_name="A",
            last_name="B",
            patronymic=None,
        )
        inviter = await user_dao.create(
            email="tdi_succ_u_inviter@example.com",
            password_hash="hash",
            student_id=student_inviter.id,
        )
        await create_team_method(CreateTeamCommand(name="Team A", user_id=inviter.id))

        # Invited user setup
        student_invited = await student_dao.create(
            student_id="tdi_succ_u_invited",
            first_name="C",
            last_name="D",
            patronymic=None,
        )
        invited = await user_dao.create(
            email="tdi_succ_u_invited@example.com",
            password_hash="hash",
            student_id=student_invited.id,
        )

        invitation = await invite_to_team_method(
            InviteToTeamCommand(user_id=inviter.id, invited_user_id=invited.id)
        )

        command = DeleteInvitationCommand(
            invitation_id=invitation.id, user_id=invited.id
        )
        await delete_invitation_method(command)

        # Calling it again should result in NotFound
        with pytest.raises(InvitationNotFoundException):
            await delete_invitation_method(command)

    async def test_delete_success_captain(
        self,
        create_team_method: CreateTeamMethod,
        invite_to_team_method: InviteToTeamMethod,
        delete_invitation_method: DeleteInvitationMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        # Inviter setup
        student_inviter = await student_dao.create(
            student_id="tdi_succ_c_inviter",
            first_name="A",
            last_name="B",
            patronymic=None,
        )
        inviter = await user_dao.create(
            email="tdi_succ_c_inviter@example.com",
            password_hash="hash",
            student_id=student_inviter.id,
        )
        await create_team_method(CreateTeamCommand(name="Team A", user_id=inviter.id))

        # Invited user setup
        student_invited = await student_dao.create(
            student_id="tdi_succ_c_invited",
            first_name="C",
            last_name="D",
            patronymic=None,
        )
        invited = await user_dao.create(
            email="tdi_succ_c_invited@example.com",
            password_hash="hash",
            student_id=student_invited.id,
        )

        invitation = await invite_to_team_method(
            InviteToTeamCommand(user_id=inviter.id, invited_user_id=invited.id)
        )

        command = DeleteInvitationCommand(
            invitation_id=invitation.id, user_id=inviter.id
        )
        await delete_invitation_method(command)

    async def test_delete_invitation_not_found(
        self,
        delete_invitation_method: DeleteInvitationMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        student = await student_dao.create(
            student_id="tdi_not_found", first_name="A", last_name="B", patronymic=None
        )
        user = await user_dao.create(
            email="tdi_not_found@example.com",
            password_hash="hash",
            student_id=student.id,
        )

        command = DeleteInvitationCommand(invitation_id=uuid4(), user_id=user.id)
        with pytest.raises(InvitationNotFoundException):
            await delete_invitation_method(command)

    async def test_delete_initiator_not_found(
        self,
        create_team_method: CreateTeamMethod,
        invite_to_team_method: InviteToTeamMethod,
        delete_invitation_method: DeleteInvitationMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        # Inviter
        student_inviter = await student_dao.create(
            student_id="tdi_init_missing_inviter",
            first_name="A",
            last_name="B",
            patronymic=None,
        )
        inviter = await user_dao.create(
            email="tdi_init_missing_inviter@example.com",
            password_hash="hash",
            student_id=student_inviter.id,
        )
        await create_team_method(CreateTeamCommand(name="Team A", user_id=inviter.id))

        # Invited
        student_invited = await student_dao.create(
            student_id="tdi_init_missing_invited",
            first_name="C",
            last_name="D",
            patronymic=None,
        )
        invited = await user_dao.create(
            email="tdi_init_missing_invited@example.com",
            password_hash="hash",
            student_id=student_invited.id,
        )

        invitation = await invite_to_team_method(
            InviteToTeamCommand(user_id=inviter.id, invited_user_id=invited.id)
        )

        command = DeleteInvitationCommand(invitation_id=invitation.id, user_id=uuid4())
        with pytest.raises(UserNotFoundException):
            await delete_invitation_method(command)

    async def test_delete_forbidden(
        self,
        create_team_method: CreateTeamMethod,
        invite_to_team_method: InviteToTeamMethod,
        delete_invitation_method: DeleteInvitationMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        # Inviter
        student_inviter = await student_dao.create(
            student_id="tdi_forb_inviter",
            first_name="A",
            last_name="B",
            patronymic=None,
        )
        inviter = await user_dao.create(
            email="tdi_forb_inviter@example.com",
            password_hash="hash",
            student_id=student_inviter.id,
        )
        await create_team_method(CreateTeamCommand(name="Team A", user_id=inviter.id))

        # Invited
        student_invited = await student_dao.create(
            student_id="tdi_forb_invited",
            first_name="C",
            last_name="D",
            patronymic=None,
        )
        invited = await user_dao.create(
            email="tdi_forb_invited@example.com",
            password_hash="hash",
            student_id=student_invited.id,
        )

        invitation = await invite_to_team_method(
            InviteToTeamCommand(user_id=inviter.id, invited_user_id=invited.id)
        )

        # Sneaky
        student_sneaky = await student_dao.create(
            student_id="tdi_sneaky", first_name="E", last_name="F", patronymic=None
        )
        sneaky = await user_dao.create(
            email="tdi_sneaky@example.com",
            password_hash="hash",
            student_id=student_sneaky.id,
        )

        command = DeleteInvitationCommand(
            invitation_id=invitation.id, user_id=sneaky.id
        )
        with pytest.raises(InvitationDeleteForbiddenException):
            await delete_invitation_method(command)

    async def test_delete_already_accepted(
        self,
        create_team_method: CreateTeamMethod,
        invite_to_team_method: InviteToTeamMethod,
        accept_invitation_method: AcceptInvitationMethod,
        delete_invitation_method: DeleteInvitationMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        # Inviter
        student_inviter = await student_dao.create(
            student_id="tdi_acc_inviter",
            first_name="A",
            last_name="B",
            patronymic=None,
        )
        inviter = await user_dao.create(
            email="tdi_acc_inviter@example.com",
            password_hash="hash",
            student_id=student_inviter.id,
        )
        await create_team_method(CreateTeamCommand(name="Team A", user_id=inviter.id))

        # Invited
        student_invited = await student_dao.create(
            student_id="tdi_acc_invited",
            first_name="C",
            last_name="D",
            patronymic=None,
        )
        invited = await user_dao.create(
            email="tdi_acc_invited@example.com",
            password_hash="hash",
            student_id=student_invited.id,
        )

        invitation = await invite_to_team_method(
            InviteToTeamCommand(user_id=inviter.id, invited_user_id=invited.id)
        )

        await accept_invitation_method(
            AcceptInvitationCommand(user_id=invited.id, invitation_id=invitation.id)
        )

        command = DeleteInvitationCommand(
            invitation_id=invitation.id, user_id=inviter.id
        )
        with pytest.raises(InvitationAlreadyAcceptedException):
            await delete_invitation_method(command)
