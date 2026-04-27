from uuid import uuid4

import pytest
from teampass.team.methods import (
    CreateTeamCommand,
    CreateTeamMethod,
    LeaveTeamCommand,
    LeaveTeamMethod,
)
from teampass.team.methods.exceptions import (
    CaptainCannotLeaveTeamException,
    TeamTransfersDisabledException,
    UserNotInTeamException,
)
from teampass.team.policies import TeamPolicies
from teampass.team.storage import TeamDAO
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import StudentDAO, UserDAO


@pytest.mark.asyncio
class TestLeaveTeamMethod:
    async def test_leave_success_member(
        self,
        create_team_method: CreateTeamMethod,
        leave_team_method: LeaveTeamMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
        team_dao: TeamDAO,
    ) -> None:
        # Captain setup
        student_cap = await student_dao.create(
            student_id="tlt_succ_m_cap", first_name="A", last_name="B", patronymic=None
        )
        captain = await user_dao.create(
            email="tlt_succ_m_cap@example.com",
            password_hash="hash",
            student_id=student_cap.id,
        )
        team = await create_team_method(
            CreateTeamCommand(name="Team", user_id=captain.id)
        )

        # Member setup
        student_mem = await student_dao.create(
            student_id="tlt_succ_m_mem", first_name="C", last_name="D", patronymic=None
        )
        member = await user_dao.create(
            email="tlt_succ_m_mem@example.com",
            password_hash="hash",
            student_id=student_mem.id,
        )
        member.team_id = team.id
        await user_dao.save(member)
        await user_dao.commit()

        command = LeaveTeamCommand(user_id=member.id)
        await leave_team_method(command)

        member_refreshed = await user_dao.find_by_id(member.id)
        assert member_refreshed is not None
        assert member_refreshed.team_id is None

        team_refreshed = await team_dao.find_by_id(team.id)
        assert team_refreshed is not None

    async def test_leave_success_sole_captain(
        self,
        create_team_method: CreateTeamMethod,
        leave_team_method: LeaveTeamMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
        team_dao: TeamDAO,
    ) -> None:
        # Captain setup
        student_cap = await student_dao.create(
            student_id="tlt_succ_c_cap", first_name="A", last_name="B", patronymic=None
        )
        captain = await user_dao.create(
            email="tlt_succ_c_cap@example.com",
            password_hash="hash",
            student_id=student_cap.id,
        )
        team = await create_team_method(
            CreateTeamCommand(name="Team", user_id=captain.id)
        )

        command = LeaveTeamCommand(user_id=captain.id)
        await leave_team_method(command)

        captain_refreshed = await user_dao.find_by_id(captain.id)
        assert captain_refreshed is not None
        assert captain_refreshed.team_id is None
        assert captain_refreshed.is_captain is False

        team_refreshed = await team_dao.find_by_id(team.id)
        assert team_refreshed is not None

    async def test_leave_user_not_found(
        self,
        leave_team_method: LeaveTeamMethod,
    ) -> None:
        command = LeaveTeamCommand(user_id=uuid4())
        with pytest.raises(UserNotFoundException):
            await leave_team_method(command)

    async def test_leave_user_not_in_team(
        self,
        leave_team_method: LeaveTeamMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        student = await student_dao.create(
            student_id="tlt_not_in_team", first_name="A", last_name="B", patronymic=None
        )
        user = await user_dao.create(
            email="tlt_not_in_team@example.com",
            password_hash="hash",
            student_id=student.id,
        )

        command = LeaveTeamCommand(user_id=user.id)
        with pytest.raises(UserNotInTeamException):
            await leave_team_method(command)

    async def test_leave_captain_cannot_leave_with_members(
        self,
        create_team_method: CreateTeamMethod,
        leave_team_method: LeaveTeamMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        # Captain setup
        student_cap = await student_dao.create(
            student_id="tlt_cap_forb_c", first_name="A", last_name="B", patronymic=None
        )
        captain = await user_dao.create(
            email="tlt_cap_forb_c@example.com",
            password_hash="hash",
            student_id=student_cap.id,
        )
        team = await create_team_method(
            CreateTeamCommand(name="Team", user_id=captain.id)
        )

        # Member setup
        student_mem = await student_dao.create(
            student_id="tlt_cap_forb_m", first_name="C", last_name="D", patronymic=None
        )
        member = await user_dao.create(
            email="tlt_cap_forb_m@example.com",
            password_hash="hash",
            student_id=student_mem.id,
        )
        member.team_id = team.id
        await user_dao.save(member)
        await user_dao.commit()

        command = LeaveTeamCommand(user_id=captain.id)
        with pytest.raises(CaptainCannotLeaveTeamException):
            await leave_team_method(command)

    async def test_leave_team_transfers_disabled(
        self,
        create_team_method: CreateTeamMethod,
        leave_team_method: LeaveTeamMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
        policies: TeamPolicies,
    ) -> None:
        student_cap = await student_dao.create(
            student_id="tlt_trans_dis", first_name="A", last_name="B", patronymic=None
        )
        captain = await user_dao.create(
            email="tlt_trans_dis@example.com",
            password_hash="hash",
            student_id=student_cap.id,
        )
        await create_team_method(CreateTeamCommand(name="Team", user_id=captain.id))

        policies.allow_team_transfers = False
        await policies.save()
        await policies.commit()

        command = LeaveTeamCommand(user_id=captain.id)
        with pytest.raises(TeamTransfersDisabledException):
            await leave_team_method(command)
