from uuid import uuid4

import pytest
from teampass.team.methods import (
    CreateTeamCommand,
    CreateTeamMethod,
    RemoveTeamMemberCommand,
    RemoveTeamMemberMethod,
)
from teampass.team.methods.exceptions import (
    CaptainCannotRemoveSelfException,
    UserNotCaptainException,
    UserNotInTeamException,
    UsersNotInSameTeamException,
)
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import StudentDAO, UserDAO


@pytest.mark.asyncio
class TestRemoveTeamMemberMethod:
    async def test_remove_success(
        self,
        create_team_method: CreateTeamMethod,
        remove_team_member_method: RemoveTeamMemberMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        # Captain setup
        student_cap = await student_dao.create(
            student_id="trm_succ_cap", first_name="A", last_name="B", patronymic=None
        )
        captain = await user_dao.create(
            email="trm_succ_cap@example.com",
            password_hash="hash",
            student_id=student_cap.id,
        )
        team = await create_team_method(
            CreateTeamCommand(name="Team", user_id=captain.id)
        )

        # Member setup
        student_mem = await student_dao.create(
            student_id="trm_succ_mem", first_name="C", last_name="D", patronymic=None
        )
        member = await user_dao.create(
            email="trm_succ_mem@example.com",
            password_hash="hash",
            student_id=student_mem.id,
        )
        member.team_id = team.id
        await user_dao.save(member)
        await user_dao.commit()

        command = RemoveTeamMemberCommand(user_id=captain.id, target_user_id=member.id)
        team_dto = await remove_team_member_method(command)

        assert len(team_dto.members) == 1
        assert team_dto.members[0].id == captain.id

        member_refreshed = await user_dao.find_by_id(member.id)
        assert member_refreshed is not None
        assert member_refreshed.team_id is None

    async def test_remove_initiator_not_found(
        self,
        remove_team_member_method: RemoveTeamMemberMethod,
    ) -> None:
        command = RemoveTeamMemberCommand(user_id=uuid4(), target_user_id=uuid4())
        with pytest.raises(UserNotFoundException):
            await remove_team_member_method(command)

    async def test_remove_initiator_not_in_team(
        self,
        remove_team_member_method: RemoveTeamMemberMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        student = await student_dao.create(
            student_id="trm_init_not_team",
            first_name="A",
            last_name="B",
            patronymic=None,
        )
        user = await user_dao.create(
            email="trm_init_not_team@example.com",
            password_hash="hash",
            student_id=student.id,
        )

        command = RemoveTeamMemberCommand(user_id=user.id, target_user_id=uuid4())
        with pytest.raises(UserNotInTeamException):
            await remove_team_member_method(command)

    async def test_remove_initiator_not_captain(
        self,
        create_team_method: CreateTeamMethod,
        remove_team_member_method: RemoveTeamMemberMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        # Captain setup
        student_cap = await student_dao.create(
            student_id="trm_not_cap_c", first_name="A", last_name="B", patronymic=None
        )
        captain = await user_dao.create(
            email="trm_not_cap_c@example.com",
            password_hash="hash",
            student_id=student_cap.id,
        )
        team = await create_team_method(
            CreateTeamCommand(name="Team", user_id=captain.id)
        )

        # Member setup
        student_mem = await student_dao.create(
            student_id="trm_not_cap_m", first_name="C", last_name="D", patronymic=None
        )
        member = await user_dao.create(
            email="trm_not_cap_m@example.com",
            password_hash="hash",
            student_id=student_mem.id,
        )
        member.team_id = team.id
        await user_dao.save(member)
        await user_dao.commit()

        command = RemoveTeamMemberCommand(user_id=member.id, target_user_id=captain.id)
        with pytest.raises(UserNotCaptainException):
            await remove_team_member_method(command)

    async def test_remove_captain_removes_self(
        self,
        create_team_method: CreateTeamMethod,
        remove_team_member_method: RemoveTeamMemberMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        student = await student_dao.create(
            student_id="trm_self", first_name="A", last_name="B", patronymic=None
        )
        captain = await user_dao.create(
            email="trm_self@example.com",
            password_hash="hash",
            student_id=student.id,
        )
        await create_team_method(CreateTeamCommand(name="Team", user_id=captain.id))

        command = RemoveTeamMemberCommand(user_id=captain.id, target_user_id=captain.id)
        with pytest.raises(CaptainCannotRemoveSelfException):
            await remove_team_member_method(command)

    async def test_remove_target_not_found(
        self,
        create_team_method: CreateTeamMethod,
        remove_team_member_method: RemoveTeamMemberMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        student = await student_dao.create(
            student_id="trm_tgt_missing", first_name="A", last_name="B", patronymic=None
        )
        captain = await user_dao.create(
            email="trm_tgt_missing@example.com",
            password_hash="hash",
            student_id=student.id,
        )
        await create_team_method(CreateTeamCommand(name="Team", user_id=captain.id))

        command = RemoveTeamMemberCommand(user_id=captain.id, target_user_id=uuid4())
        with pytest.raises(UserNotFoundException):
            await remove_team_member_method(command)

    async def test_remove_target_not_in_same_team(
        self,
        create_team_method: CreateTeamMethod,
        remove_team_member_method: RemoveTeamMemberMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        student_cap = await student_dao.create(
            student_id="trm_diff_cap", first_name="A", last_name="B", patronymic=None
        )
        captain = await user_dao.create(
            email="trm_diff_cap@example.com",
            password_hash="hash",
            student_id=student_cap.id,
        )
        await create_team_method(CreateTeamCommand(name="Team A", user_id=captain.id))

        student_other = await student_dao.create(
            student_id="trm_diff_oth", first_name="C", last_name="D", patronymic=None
        )
        other = await user_dao.create(
            email="trm_diff_oth@example.com",
            password_hash="hash",
            student_id=student_other.id,
        )
        await create_team_method(CreateTeamCommand(name="Team B", user_id=other.id))

        command = RemoveTeamMemberCommand(user_id=captain.id, target_user_id=other.id)
        with pytest.raises(UsersNotInSameTeamException):
            await remove_team_member_method(command)
