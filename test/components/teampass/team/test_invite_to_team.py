from uuid import uuid4

import pytest
from teampass.team.methods import (
    CreateTeamCommand,
    CreateTeamMethod,
    InviteToTeamCommand,
    InviteToTeamMethod,
)
from teampass.team.methods.exceptions import (
    InvitationAlreadyExistsException,
    UserAlreadyInTeamException,
    UserNotCaptainException,
    UserNotInTeamException,
)
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import StudentDAO, UserDAO


@pytest.mark.asyncio
class TestInviteToTeamMethod:
    async def test_invite_success(
        self,
        create_team_method: CreateTeamMethod,
        invite_to_team_method: InviteToTeamMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        # Inviter setup
        student_inviter = await student_dao.create(
            student_id="tit_success_inviter",
            first_name="A",
            last_name="B",
            patronymic=None,
        )
        inviter = await user_dao.create(
            email="tit_success_inviter@example.com",
            password_hash="hash",
            student_id=student_inviter.id,
        )
        await create_team_method(CreateTeamCommand(name="Team A", user_id=inviter.id))

        # Invited user setup
        student_invited = await student_dao.create(
            student_id="tit_success_invited",
            first_name="C",
            last_name="D",
            patronymic=None,
        )
        invited = await user_dao.create(
            email="tit_success_invited@example.com",
            password_hash="hash",
            student_id=student_invited.id,
        )

        command = InviteToTeamCommand(inviter_id=inviter.id, invited_user_id=invited.id)
        invitation_dto = await invite_to_team_method(command)

        assert invitation_dto is not None
        assert invitation_dto.user.id == invited.id
        inviter_refreshed = await user_dao.find_by_id(inviter.id)
        assert inviter_refreshed is not None
        assert invitation_dto.team.id == inviter_refreshed.team_id
        assert invitation_dto.accepted_at is None

    async def test_inviter_not_found(
        self,
        invite_to_team_method: InviteToTeamMethod,
    ) -> None:
        command = InviteToTeamCommand(inviter_id=uuid4(), invited_user_id=uuid4())
        with pytest.raises(UserNotFoundException) as exc_info:
            await invite_to_team_method(command)
        assert exc_info.value.user_id == command.inviter_id

    async def test_inviter_not_in_team(
        self,
        invite_to_team_method: InviteToTeamMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        student = await student_dao.create(
            student_id="tit_not_in_team", first_name="A", last_name="B", patronymic=None
        )
        inviter = await user_dao.create(
            email="tit_not_in_team@example.com",
            password_hash="hash",
            student_id=student.id,
        )

        command = InviteToTeamCommand(inviter_id=inviter.id, invited_user_id=uuid4())
        with pytest.raises(UserNotInTeamException) as exc_info:
            await invite_to_team_method(command)
        assert exc_info.value.user_id == inviter.id

    async def test_inviter_not_captain(
        self,
        create_team_method: CreateTeamMethod,
        invite_to_team_method: InviteToTeamMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        student_captain = await student_dao.create(
            student_id="tit_not_cap_c", first_name="A", last_name="B", patronymic=None
        )
        captain = await user_dao.create(
            email="tit_not_cap_c@example.com",
            password_hash="hash",
            student_id=student_captain.id,
        )
        team_dto = await create_team_method(
            CreateTeamCommand(name="Team", user_id=captain.id)
        )

        student_member = await student_dao.create(
            student_id="tit_not_cap_m", first_name="A", last_name="B", patronymic=None
        )
        member = await user_dao.create(
            email="tit_not_cap_m@example.com",
            password_hash="hash",
            student_id=student_member.id,
        )
        member.team_id = team_dto.id
        await user_dao.save(member)
        await user_dao.commit()

        command = InviteToTeamCommand(inviter_id=member.id, invited_user_id=uuid4())
        with pytest.raises(UserNotCaptainException) as exc_info:
            await invite_to_team_method(command)
        assert exc_info.value.user_id == member.id

    async def test_invited_user_not_found(
        self,
        create_team_method: CreateTeamMethod,
        invite_to_team_method: InviteToTeamMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        student_inviter = await student_dao.create(
            student_id="tit_target_missing",
            first_name="A",
            last_name="B",
            patronymic=None,
        )
        inviter = await user_dao.create(
            email="tit_target_missing@example.com",
            password_hash="hash",
            student_id=student_inviter.id,
        )
        await create_team_method(CreateTeamCommand(name="Team A", user_id=inviter.id))

        fake_invited_id = uuid4()
        command = InviteToTeamCommand(
            inviter_id=inviter.id, invited_user_id=fake_invited_id
        )
        with pytest.raises(UserNotFoundException) as exc_info:
            await invite_to_team_method(command)
        assert exc_info.value.user_id == fake_invited_id

    async def test_invited_already_in_team(
        self,
        create_team_method: CreateTeamMethod,
        invite_to_team_method: InviteToTeamMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        student_inviter = await student_dao.create(
            student_id="tit_already_in_team_i",
            first_name="A",
            last_name="B",
            patronymic=None,
        )
        inviter = await user_dao.create(
            email="tit_already_in_team_i@example.com",
            password_hash="hash",
            student_id=student_inviter.id,
        )
        await create_team_method(CreateTeamCommand(name="Team A", user_id=inviter.id))

        student_invited = await student_dao.create(
            student_id="tit_already_in_team_u",
            first_name="A",
            last_name="B",
            patronymic=None,
        )
        invited = await user_dao.create(
            email="tit_already_in_team_u@example.com",
            password_hash="hash",
            student_id=student_invited.id,
        )
        await create_team_method(CreateTeamCommand(name="Team B", user_id=invited.id))

        command = InviteToTeamCommand(inviter_id=inviter.id, invited_user_id=invited.id)
        with pytest.raises(UserAlreadyInTeamException) as exc_info:
            await invite_to_team_method(command)
        assert exc_info.value.user_id == invited.id

    async def test_invitation_already_exists(
        self,
        create_team_method: CreateTeamMethod,
        invite_to_team_method: InviteToTeamMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        student_inviter = await student_dao.create(
            student_id="tit_dup_inviter", first_name="A", last_name="B", patronymic=None
        )
        inviter = await user_dao.create(
            email="tit_dup_inviter@example.com",
            password_hash="hash",
            student_id=student_inviter.id,
        )
        await create_team_method(CreateTeamCommand(name="Team A", user_id=inviter.id))

        student_invited = await student_dao.create(
            student_id="tit_dup_invited", first_name="C", last_name="D", patronymic=None
        )
        invited = await user_dao.create(
            email="tit_dup_invited@example.com",
            password_hash="hash",
            student_id=student_invited.id,
        )

        command = InviteToTeamCommand(inviter_id=inviter.id, invited_user_id=invited.id)
        await invite_to_team_method(command)

        with pytest.raises(InvitationAlreadyExistsException) as exc_info:
            await invite_to_team_method(command)
        assert exc_info.value.user_id == invited.id
