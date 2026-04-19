from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from enum import StrEnum
from typing import override
from uuid import UUID

from sqlalchemy import ForeignKey, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, joinedload, mapped_column, relationship
from sqlalchemy.orm.interfaces import ORMOption
from sqlalchemy.types import TIMESTAMP
from teampass.database import BaseDAO, BaseDAOFactory, BaseModel
from teampass.user.storage import User

from .team import Team


class TeamInvitation(BaseModel):
    __tablename__: str = "team_invitation"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), index=True
    )
    team_id: Mapped[UUID] = mapped_column(
        ForeignKey("team.id", ondelete="CASCADE"), index=True
    )
    accepted_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), default=None
    )

    user: Mapped[User] = relationship(back_populates="invitations")
    team: Mapped[Team] = relationship(back_populates="invitations")


class TeamInvitationLoadEnum(StrEnum):
    USER = "user"
    TEAM_WITH_MEMBERS = "team_with_members"


class TeamInvitationDAO(BaseDAO[TeamInvitation, UUID, TeamInvitationLoadEnum]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TeamInvitation)

    @property
    @override
    def _load_mapper(
        self,
    ) -> dict[TeamInvitationLoadEnum, ORMOption | Sequence[ORMOption]]:
        return {
            TeamInvitationLoadEnum.USER: joinedload(TeamInvitation.user).joinedload(
                User.student
            ),
            TeamInvitationLoadEnum.TEAM_WITH_MEMBERS: joinedload(TeamInvitation.team)
            .selectinload(Team.members)
            .joinedload(User.student),
        }

    async def create(
        self,
        user_id: UUID,
        team_id: UUID,
    ) -> TeamInvitation:
        obj = TeamInvitation(user_id=user_id, team_id=team_id)
        await self.save(obj)
        return obj

    async def find_by_user_and_team(
        self,
        user_id: UUID,
        team_id: UUID,
        includes: list[TeamInvitationLoadEnum] | None = None,
    ) -> TeamInvitation | None:
        stmt = select(TeamInvitation).where(
            TeamInvitation.user_id == user_id,
            TeamInvitation.team_id == team_id,
        )
        if includes is not None:
            stmt = stmt.options(*self.get_options(includes))
            stmt = stmt.execution_options(populate_existing=True)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()


class TeamInvitationDAOFactory(BaseDAOFactory[TeamInvitationDAO]):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_maker, TeamInvitationDAO)
