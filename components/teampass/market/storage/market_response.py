from __future__ import annotations

from collections.abc import Sequence
from enum import StrEnum
from typing import TYPE_CHECKING, Any, override
from uuid import UUID

from sqlalchemy import ForeignKey, Index, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, joinedload, mapped_column, relationship
from sqlalchemy.orm.interfaces import ORMOption
from teampass.database import BaseDAO, BaseDAOFactory, BaseModel
from teampass.team.storage import Team
from teampass.user.storage import User

if TYPE_CHECKING:
    from .market_deal import MarketDeal
    from .market_listing import MarketListing


class MarketResponseStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class MarketResponse(BaseModel):
    __tablename__: str = "market_response"
    __table_args__: tuple[Any, ...] = (
        Index(
            "uq_market_response_one_accepted_per_listing",
            "market_listing_id",
            unique=True,
            postgresql_where="status = 'ACCEPTED'",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    responder_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), index=True
    )
    team_id: Mapped[UUID] = mapped_column(
        ForeignKey("team.id", ondelete="CASCADE"), index=True
    )
    market_listing_id: Mapped[UUID] = mapped_column(
        ForeignKey("market_listing.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[MarketResponseStatus] = mapped_column(
        default=MarketResponseStatus.PENDING
    )

    responder: Mapped[User] = relationship()
    team: Mapped[Team] = relationship(back_populates="market_responses")
    market_listing: Mapped[MarketListing] = relationship(
        back_populates="market_responses"
    )
    market_deal: Mapped[MarketDeal] = relationship(
        back_populates="market_response",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class MarketResponseLoadEnum(StrEnum):
    RESPONDER = "responder"
    TEAM = "team"
    MARKET_LISTING = "market_listing"


class MarketResponseDAO(BaseDAO[MarketResponse, UUID, MarketResponseLoadEnum]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, MarketResponse)

    @property
    @override
    def _load_mapper(
        self,
    ) -> dict[MarketResponseLoadEnum, ORMOption | Sequence[ORMOption]]:
        return {
            MarketResponseLoadEnum.RESPONDER: joinedload(MarketResponse.responder),
            MarketResponseLoadEnum.TEAM: (
                joinedload(MarketResponse.team)
                .selectinload(Team.members)
                .joinedload(User.student)
            ),
            MarketResponseLoadEnum.MARKET_LISTING: joinedload(
                MarketResponse.market_listing
            ),
        }

    async def create(
        self,
        responder_id: UUID,
        team_id: UUID,
        market_listing_id: UUID,
        status: MarketResponseStatus = MarketResponseStatus.PENDING,
    ) -> MarketResponse:
        obj = MarketResponse(
            responder_id=responder_id,
            team_id=team_id,
            market_listing_id=market_listing_id,
            status=status,
        )
        await self.save(obj)
        return obj

    async def find_by_listing_id(
        self,
        market_listing_id: UUID,
        includes: list[MarketResponseLoadEnum] | None = None,
    ) -> list[MarketResponse]:
        stmt = select(MarketResponse).where(
            MarketResponse.market_listing_id == market_listing_id
        )
        if includes is not None:
            stmt = stmt.options(*self.get_options(includes))
            stmt = stmt.execution_options(populate_existing=True)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def reject_others_for_listing(
        self,
        market_listing_id: UUID,
        accepted_response_id: UUID,
    ) -> None:
        stmt = (
            update(MarketResponse)
            .where(
                MarketResponse.market_listing_id == market_listing_id,
                MarketResponse.id != accepted_response_id,
            )
            .values(status=MarketResponseStatus.REJECTED)
        )
        await self._session.execute(stmt)

    async def find_by_team_id(
        self,
        team_id: UUID,
        includes: list[MarketResponseLoadEnum] | None = None,
    ) -> list[MarketResponse]:
        stmt = select(MarketResponse).where(MarketResponse.team_id == team_id)
        if includes is not None:
            stmt = stmt.options(*self.get_options(includes))
            stmt = stmt.execution_options(populate_existing=True)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


class MarketResponseDAOFactory(BaseDAOFactory[MarketResponseDAO]):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_maker, MarketResponseDAO)
