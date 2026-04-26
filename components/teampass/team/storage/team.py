from __future__ import annotations

from collections.abc import Sequence
from enum import StrEnum
from typing import TYPE_CHECKING, override
from uuid import UUID

from sqlalchemy import String, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from sqlalchemy.orm.interfaces import ORMOption
from teampass.database import BaseDAO, BaseDAOFactory, BaseModel
from teampass.user.storage import User

if TYPE_CHECKING:
    from teampass.transaction.storage import CycleSnapshot, PointTransaction

    from .invitation import TeamInvitation


class Team(BaseModel):
    __tablename__: str = "team"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(String(255))

    members: Mapped[list[User]] = relationship(
        back_populates="team", passive_deletes=True
    )
    invitations: Mapped[list[TeamInvitation]] = relationship(
        back_populates="team", cascade="all, delete-orphan", passive_deletes=True
    )
    point_transactions: Mapped[list[PointTransaction]] = relationship(
        back_populates="team", cascade="all, delete-orphan", passive_deletes=True
    )
    cycle_snapshots: Mapped[list[CycleSnapshot]] = relationship(
        back_populates="team", cascade="all, delete-orphan", passive_deletes=True
    )

    @property
    def captain(self) -> User | None:
        return next((m for m in self.members if m.is_captain), None)


class TeamLoadEnum(StrEnum):
    MEMBERS = "members"
    INVITATIONS = "invitations"


class TeamDAO(BaseDAO[Team, UUID, TeamLoadEnum]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Team)

    @property
    @override
    def _load_mapper(self) -> dict[TeamLoadEnum, ORMOption | Sequence[ORMOption]]:
        return {
            TeamLoadEnum.MEMBERS: selectinload(Team.members).joinedload(User.student),
            TeamLoadEnum.INVITATIONS: selectinload(Team.invitations),
        }

    async def create(
        self,
        name: str,
    ) -> Team:
        obj = Team(name=name)
        await self.save(obj)
        return obj

    async def find_by_user_id(
        self, user_id: UUID, includes: list[TeamLoadEnum] | None = None
    ) -> Team | None:
        stmt = select(Team).where(Team.members.any(User.id == user_id))
        if includes is not None:
            stmt = stmt.options(*self.get_options(includes))
            stmt = stmt.execution_options(populate_existing=True)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()


class TeamDAOFactory(BaseDAOFactory[TeamDAO]):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_maker, TeamDAO)
