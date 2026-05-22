from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest
import pytest_asyncio
from dishka import AsyncContainer, Provider, make_async_container
from teampass.database import DatabaseProvider
from teampass.market import MarketProvider
from teampass.media_storage import MediaStorageProvider
from teampass.report import ReportProvider
from teampass.team import TeamProvider
from teampass.team.storage import Team, TeamDAO
from teampass.transaction import TransactionProvider
from teampass.transaction.storage import GameCycle, GameCycleDAO
from teampass.user import UserProvider
from teampass.user.storage import StudentDAO, User, UserDAO


@pytest_asyncio.fixture(scope="class")
async def app_container(
    test_database_provider: Provider,
) -> AsyncIterator[AsyncContainer]:
    container = make_async_container(
        DatabaseProvider(),
        test_database_provider,
        UserProvider(),
        TeamProvider(),
        TransactionProvider(),
        MediaStorageProvider(),
        ReportProvider(),
        MarketProvider(),
    )
    yield container
    await container.close()


class UtilsForTesting:
    def __init__(self, request_container: AsyncContainer) -> None:
        self.request_container: AsyncContainer = request_container

    async def create_user(
        self,
        email: str,
        student_id: str,
        team_id: UUID | None = None,
        is_captain: bool = False,
    ) -> User:
        student_dao = await self.request_container.get(StudentDAO)
        user_dao = await self.request_container.get(UserDAO)
        student = await student_dao.create(
            student_id=student_id,
            first_name="Test",
            last_name="User",
            patronymic=None,
        )
        user = await user_dao.create(
            email=email,
            password_hash="hash",
            student_id=student.id,
        )
        if team_id is not None:
            user.team_id = team_id
            user.is_captain = is_captain
            await user_dao.save(user)
        await user_dao.commit()
        return user

    async def create_team(self, name: str) -> Team:
        team_dao = await self.request_container.get(TeamDAO)
        team = await team_dao.create(name=name)
        await team_dao.commit()
        return team

    async def create_game_cycle(self) -> GameCycle:
        game_cycle_dao = await self.request_container.get(GameCycleDAO)
        now = datetime.now(timezone.utc)
        existing = await game_cycle_dao.find_overlapping(now, now)
        if existing is not None:
            return existing

        cycle = await game_cycle_dao.create(
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=1),
        )
        await game_cycle_dao.commit()
        return cycle


@pytest.fixture
def factory(request_container: AsyncContainer) -> UtilsForTesting:
    return UtilsForTesting(request_container)
