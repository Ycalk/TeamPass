from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import String, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TIMESTAMP

from ._base import BaseDAO, BaseDAOFactory, BaseModel

if TYPE_CHECKING:
    from .user import User


class Team(BaseModel):
    __tablename__: str = "team"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    members: Mapped[list[User]] = relationship(back_populates="team")
    captain: Mapped[User | None] = relationship(
        primaryjoin="and_(Team.id == User.team_id, User.is_captain == True)",
        viewonly=True,
    )


class TeamDAO(BaseDAO[Team, UUID]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Team)

    async def create(
        self,
        name: str,
    ) -> Team:
        obj = Team(name=name)
        await self.save(obj)
        return obj


class TeamDAOFactory(BaseDAOFactory[TeamDAO]):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_maker, TeamDAO)
