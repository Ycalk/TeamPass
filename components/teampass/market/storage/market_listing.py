from __future__ import annotations

from collections.abc import Sequence
from enum import StrEnum
from typing import TYPE_CHECKING, override
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, joinedload, mapped_column, relationship
from sqlalchemy.orm.interfaces import ORMOption
from teampass.database import BaseDAO, BaseDAOFactory, BaseModel

if TYPE_CHECKING:
    from teampass.team.storage import Team
    from teampass.transaction.storage import GameCycle
    from teampass.user.storage import User

    from .market_response import MarketResponse


class MarketListing(BaseModel):
    __tablename__: str = "market_listing"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    author_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), index=True
    )
    team_id: Mapped[UUID] = mapped_column(
        ForeignKey("team.id", ondelete="CASCADE"), index=True
    )
    game_cycle_id: Mapped[UUID] = mapped_column(
        ForeignKey("game_cycle.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)

    author: Mapped[User] = relationship()
    team: Mapped[Team] = relationship(back_populates="market_listings")
    game_cycle: Mapped[GameCycle] = relationship(back_populates="market_listings")
    market_responses: Mapped[list[MarketResponse]] = relationship(
        back_populates="market_listing",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class MarketListingLoadEnum(StrEnum):
    AUTHOR = "author"
    TEAM = "team"
    GAME_CYCLE = "game_cycle"


class MarketListingDAO(BaseDAO[MarketListing, UUID, MarketListingLoadEnum]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, MarketListing)

    @property
    @override
    def _load_mapper(
        self,
    ) -> dict[MarketListingLoadEnum, ORMOption | Sequence[ORMOption]]:
        return {
            MarketListingLoadEnum.AUTHOR: joinedload(MarketListing.author),
            MarketListingLoadEnum.TEAM: joinedload(MarketListing.team),
            MarketListingLoadEnum.GAME_CYCLE: joinedload(MarketListing.game_cycle),
        }

    async def create(
        self,
        title: str,
        description: str,
        team_id: UUID,
        game_cycle_id: UUID,
        author_id: UUID,
    ) -> MarketListing:
        obj = MarketListing(
            title=title,
            description=description,
            team_id=team_id,
            game_cycle_id=game_cycle_id,
            author_id=author_id,
        )
        await self.save(obj)
        return obj


class MarketListingDAOFactory(BaseDAOFactory[MarketListingDAO]):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_maker, MarketListingDAO)
