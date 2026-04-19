from uuid import uuid4

import pytest
from teampass.team.methods import (
    CreateTeamCommand,
    CreateTeamMethod,
    TransferCaptaincyCommand,
    TransferCaptaincyMethod,
)
from teampass.team.methods.exceptions import (
    UserNotCaptainException,
    UserNotInTeamException,
    UsersNotInSameTeamException,
)
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import StudentDAO, UserDAO


@pytest.mark.asyncio
class TestTransferCaptaincyMethod:
    async def test_transfer_success(
        self,
        create_team_method: CreateTeamMethod,
        transfer_captaincy_method: TransferCaptaincyMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        # Captain setup
        student_cap = await student_dao.create(
            student_id="ttc_succ_cap", first_name="A", last_name="B", patronymic=None
        )
        captain = await user_dao.create(
            email="ttc_succ_cap@example.com",
            password_hash="hash",
            student_id=student_cap.id,
        )
        team = await create_team_method(
            CreateTeamCommand(name="Team", user_id=captain.id)
        )

        # Member setup
        student_mem = await student_dao.create(
            student_id="ttc_succ_mem", first_name="C", last_name="D", patronymic=None
        )
        member = await user_dao.create(
            email="ttc_succ_mem@example.com",
            password_hash="hash",
            student_id=student_mem.id,
        )
        member.team_id = team.id
        await user_dao.save(member)
        await user_dao.commit()

        command = TransferCaptaincyCommand(
            initiator_id=captain.id, new_captain_id=member.id
        )
        team_dto = await transfer_captaincy_method(command)

        assert team_dto.captain is not None
        assert team_dto.captain.id == member.id

        captain_refreshed = await user_dao.find_by_id(captain.id)
        assert captain_refreshed is not None
        assert captain_refreshed.is_captain is False

        member_refreshed = await user_dao.find_by_id(member.id)
        assert member_refreshed is not None
        assert member_refreshed.is_captain is True

    async def test_transfer_initiator_not_found(
        self,
        transfer_captaincy_method: TransferCaptaincyMethod,
    ) -> None:
        command = TransferCaptaincyCommand(initiator_id=uuid4(), new_captain_id=uuid4())
        with pytest.raises(UserNotFoundException):
            await transfer_captaincy_method(command)

    async def test_transfer_initiator_not_in_team(
        self,
        transfer_captaincy_method: TransferCaptaincyMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        student = await student_dao.create(
            student_id="ttc_init_not_team",
            first_name="A",
            last_name="B",
            patronymic=None,
        )
        user = await user_dao.create(
            email="ttc_init_not_team@example.com",
            password_hash="hash",
            student_id=student.id,
        )

        command = TransferCaptaincyCommand(initiator_id=user.id, new_captain_id=uuid4())
        with pytest.raises(UserNotInTeamException):
            await transfer_captaincy_method(command)

    async def test_transfer_initiator_not_captain(
        self,
        create_team_method: CreateTeamMethod,
        transfer_captaincy_method: TransferCaptaincyMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        # Captain setup
        student_cap = await student_dao.create(
            student_id="ttc_not_cap_c", first_name="A", last_name="B", patronymic=None
        )
        captain = await user_dao.create(
            email="ttc_not_cap_c@example.com",
            password_hash="hash",
            student_id=student_cap.id,
        )
        team = await create_team_method(
            CreateTeamCommand(name="Team", user_id=captain.id)
        )

        # Member setup
        student_mem = await student_dao.create(
            student_id="ttc_not_cap_m", first_name="C", last_name="D", patronymic=None
        )
        member = await user_dao.create(
            email="ttc_not_cap_m@example.com",
            password_hash="hash",
            student_id=student_mem.id,
        )
        member.team_id = team.id
        await user_dao.save(member)
        await user_dao.commit()

        command = TransferCaptaincyCommand(
            initiator_id=member.id, new_captain_id=captain.id
        )
        with pytest.raises(UserNotCaptainException):
            await transfer_captaincy_method(command)

    async def test_transfer_new_captain_not_found(
        self,
        create_team_method: CreateTeamMethod,
        transfer_captaincy_method: TransferCaptaincyMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        student = await student_dao.create(
            student_id="ttc_new_missing", first_name="A", last_name="B", patronymic=None
        )
        captain = await user_dao.create(
            email="ttc_new_missing@example.com",
            password_hash="hash",
            student_id=student.id,
        )
        await create_team_method(CreateTeamCommand(name="Team", user_id=captain.id))

        command = TransferCaptaincyCommand(
            initiator_id=captain.id, new_captain_id=uuid4()
        )
        with pytest.raises(UserNotFoundException):
            await transfer_captaincy_method(command)

    async def test_transfer_new_captain_not_in_same_team(
        self,
        create_team_method: CreateTeamMethod,
        transfer_captaincy_method: TransferCaptaincyMethod,
        student_dao: StudentDAO,
        user_dao: UserDAO,
    ) -> None:
        student_cap = await student_dao.create(
            student_id="ttc_diff_cap", first_name="A", last_name="B", patronymic=None
        )
        captain = await user_dao.create(
            email="ttc_diff_cap@example.com",
            password_hash="hash",
            student_id=student_cap.id,
        )
        await create_team_method(CreateTeamCommand(name="Team A", user_id=captain.id))

        student_other = await student_dao.create(
            student_id="ttc_diff_oth", first_name="C", last_name="D", patronymic=None
        )
        other = await user_dao.create(
            email="ttc_diff_oth@example.com",
            password_hash="hash",
            student_id=student_other.id,
        )
        await create_team_method(CreateTeamCommand(name="Team B", user_id=other.id))

        command = TransferCaptaincyCommand(
            initiator_id=captain.id, new_captain_id=other.id
        )
        with pytest.raises(UsersNotInSameTeamException):
            await transfer_captaincy_method(command)
