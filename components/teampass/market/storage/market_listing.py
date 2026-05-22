from __future__ import annotations

from collections.abc import Sequence
from enum import StrEnum
from typing import TYPE_CHECKING, override
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, joinedload, mapped_column, relationship, selectinload
from sqlalchemy.orm.interfaces import ORMOption
from teampass.database import BaseDAO, BaseDAOFactory, BaseModel
from teampass.team.storage import Team
from teampass.user.storage import User

if TYPE_CHECKING:
    from teampass.transaction.storage import GameCycle

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
    MARKET_RESPONSES = "market_responses"


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
            MarketListingLoadEnum.TEAM: (
                joinedload(MarketListing.team)
                .selectinload(Team.members)
                .joinedload(User.student)
            ),
            MarketListingLoadEnum.GAME_CYCLE: joinedload(MarketListing.game_cycle),
            MarketListingLoadEnum.MARKET_RESPONSES: selectinload(
                MarketListing.market_responses
            ),
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

    async def count_by_team_and_cycle(
        self,
        team_id: UUID,
        game_cycle_id: UUID,
    ) -> int:
        stmt = select(func.count()).where(
            MarketListing.team_id == team_id,
            MarketListing.game_cycle_id == game_cycle_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def find_without_deals(
        self,
        includes: list[MarketListingLoadEnum] | None = None,
    ) -> list[MarketListing]:
        from .market_response import MarketResponse, MarketResponseStatus

        subq = (
            select(MarketListing.id)
            .join(MarketResponse, MarketResponse.market_listing_id == MarketListing.id)
            .where(MarketResponse.status == MarketResponseStatus.ACCEPTED)
            .scalar_subquery()
        )
        stmt = select(MarketListing).where(~MarketListing.id.in_(subq))
        if includes is not None:
            stmt = stmt.options(*self.get_options(includes))
            stmt = stmt.execution_options(populate_existing=True)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_team_id(
        self,
        team_id: UUID,
        includes: list[MarketListingLoadEnum] | None = None,
    ) -> list[MarketListing]:
        stmt = select(MarketListing).where(MarketListing.team_id == team_id)
        if includes is not None:
            stmt = stmt.options(*self.get_options(includes))
            stmt = stmt.execution_options(populate_existing=True)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_completed_by_team_and_cycle(
        self,
        team_id: UUID,
        game_cycle_id: UUID,
    ) -> int:
        from .market_deal import MarketDeal, MarketDealStatus
        from .market_response import MarketResponse

        stmt = (
            select(func.count())
            .select_from(MarketListing)
            .join(MarketResponse, MarketResponse.market_listing_id == MarketListing.id)
            .join(MarketDeal, MarketDeal.market_response_id == MarketResponse.id)
            .where(
                MarketListing.team_id == team_id,
                MarketListing.game_cycle_id == game_cycle_id,
                MarketDeal.status == MarketDealStatus.COMPLETED,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def count_without_deals_by_team_and_cycle(
        self,
        team_id: UUID,
        game_cycle_id: UUID,
    ) -> int:
        from .market_response import MarketResponse, MarketResponseStatus

        subq = (
            select(MarketListing.id)
            .join(MarketResponse, MarketResponse.market_listing_id == MarketListing.id)
            .where(MarketResponse.status == MarketResponseStatus.ACCEPTED)
            .scalar_subquery()
        )
        stmt = select(func.count()).where(
            MarketListing.team_id == team_id,
            MarketListing.game_cycle_id == game_cycle_id,
            ~MarketListing.id.in_(subq),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()


class MarketListingDAOFactory(BaseDAOFactory[MarketListingDAO]):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_maker, MarketListingDAO)
