from uuid import uuid4

import pytest
from teampass.team.methods import (
    CreateTeamCommand,
    CreateTeamMethod,
)
from teampass.team.methods.exceptions import (
    TeamTransfersDisabledException,
    UserAlreadyInTeamException,
)
from teampass.team.policies import TeamPolicies
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import StudentDAO, UserDAO


@pytest.mark.asyncio
class TestCreateTeamMethod:
    async def test_create_team_success(
        self,
        create_team_method: CreateTeamMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        student = await student_dao.create(
            student_id="tct_success",
            first_name="Test",
            last_name="Testov",
            patronymic=None,
        )
        user = await user_dao.create(
            email="tct_success@example.com",
            password_hash="hash",
            student_id=student.id,
        )

        command = CreateTeamCommand(name="Super Team", user_id=user.id)
        team_dto = await create_team_method(command)

        assert team_dto is not None
        assert team_dto.name == "Super Team"
        assert len(team_dto.members) == 1
        assert team_dto.members[0].id == user.id
        assert team_dto.captain is not None
        assert team_dto.captain.id == user.id

        updated_user = await user_dao.find_by_id(user.id)
        assert updated_user is not None
        assert updated_user.team_id == team_dto.id
        assert updated_user.is_captain is True

    async def test_create_team_user_not_found(
        self,
        create_team_method: CreateTeamMethod,
    ) -> None:
        fake_id = uuid4()
        command = CreateTeamCommand(name="Ghost Team", user_id=fake_id)

        with pytest.raises(UserNotFoundException) as exc_info:
            await create_team_method(command)

        assert exc_info.value.user_id == fake_id

    async def test_create_team_user_already_in_team(
        self,
        create_team_method: CreateTeamMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        student = await student_dao.create(
            student_id="tct_already",
            first_name="Test",
            last_name="Testov",
            patronymic=None,
        )
        user = await user_dao.create(
            email="tct_already@example.com",
            password_hash="hash",
            student_id=student.id,
        )

        command1 = CreateTeamCommand(name="First Team", user_id=user.id)
        await create_team_method(command1)

        command2 = CreateTeamCommand(name="Second Team", user_id=user.id)
        with pytest.raises(UserAlreadyInTeamException) as exc_info:
            await create_team_method(command2)

        assert exc_info.value.user_id == user.id

    async def test_create_team_transfers_disabled(
        self,
        create_team_method: CreateTeamMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
        policies: TeamPolicies,
    ) -> None:
        policies.allow_team_transfers = False
        await policies.save()
        await policies.commit()

        student = await student_dao.create(
            student_id="tct_no_transfer",
            first_name="Test",
            last_name="Testov",
            patronymic=None,
        )
        user = await user_dao.create(
            email="tct_notransfer@example.com",
            password_hash="hash",
            student_id=student.id,
        )

        command = CreateTeamCommand(name="No Transfer Team", user_id=user.id)
        with pytest.raises(TeamTransfersDisabledException):
            await create_team_method(command)
