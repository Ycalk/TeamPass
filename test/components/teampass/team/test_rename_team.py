from uuid import uuid4

import pytest
from teampass.team.methods import (
    CreateTeamCommand,
    CreateTeamMethod,
    RenameTeamCommand,
    RenameTeamMethod,
)
from teampass.team.methods.exceptions import (
    UserNotCaptainException,
    UserNotInTeamException,
)
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import StudentDAO, UserDAO


@pytest.mark.asyncio
class TestRenameTeamMethod:
    async def test_rename_success(
        self,
        create_team_method: CreateTeamMethod,
        rename_team_method: RenameTeamMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        student_cap = await student_dao.create(
            student_id="trt_succ_cap", first_name="A", last_name="B", patronymic=None
        )
        captain = await user_dao.create(
            email="trt_succ_cap@example.com",
            password_hash="hash",
            student_id=student_cap.id,
        )
        team = await create_team_method(
            CreateTeamCommand(name="Old Name", user_id=captain.id)
        )

        command = RenameTeamCommand(name="New Name", user_id=captain.id)
        team_dto = await rename_team_method(command)

        assert team_dto.id == team.id
        assert team_dto.name == "New Name"

    async def test_rename_initiator_not_found(
        self,
        rename_team_method: RenameTeamMethod,
    ) -> None:
        command = RenameTeamCommand(name="New Name", user_id=uuid4())
        with pytest.raises(UserNotFoundException):
            await rename_team_method(command)

    async def test_rename_initiator_not_in_team(
        self,
        rename_team_method: RenameTeamMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        student = await student_dao.create(
            student_id="trt_not_in_team", first_name="A", last_name="B", patronymic=None
        )
        user = await user_dao.create(
            email="trt_not_in_team@example.com",
            password_hash="hash",
            student_id=student.id,
        )

        command = RenameTeamCommand(name="New Name", user_id=user.id)
        with pytest.raises(UserNotInTeamException):
            await rename_team_method(command)

    async def test_rename_initiator_not_captain(
        self,
        create_team_method: CreateTeamMethod,
        rename_team_method: RenameTeamMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        # Captain
        student_cap = await student_dao.create(
            student_id="trt_not_cap_c", first_name="A", last_name="B", patronymic=None
        )
        captain = await user_dao.create(
            email="trt_not_cap_c@example.com",
            password_hash="hash",
            student_id=student_cap.id,
        )
        team = await create_team_method(
            CreateTeamCommand(name="Team", user_id=captain.id)
        )

        # Member
        student_mem = await student_dao.create(
            student_id="trt_not_cap_m", first_name="C", last_name="D", patronymic=None
        )
        member = await user_dao.create(
            email="trt_not_cap_m@example.com",
            password_hash="hash",
            student_id=student_mem.id,
        )
        member.team_id = team.id
        await user_dao.save(member)
        await user_dao.commit()

        command = RenameTeamCommand(name="New Name", user_id=member.id)
        with pytest.raises(UserNotCaptainException):
            await rename_team_method(command)
