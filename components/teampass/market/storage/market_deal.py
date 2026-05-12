from __future__ import annotations

from collections.abc import Sequence
from enum import StrEnum
from typing import TYPE_CHECKING, override
from uuid import UUID

from sqlalchemy import ForeignKey, func, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, joinedload, mapped_column, relationship
from sqlalchemy.orm.interfaces import ORMOption
from teampass.database import BaseDAO, BaseDAOFactory, BaseModel

if TYPE_CHECKING:
    from teampass.report.storage import Report

    from .market_response import MarketResponse


class MarketDealStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class MarketDeal(BaseModel):
    __tablename__: str = "market_deal"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    market_response_id: Mapped[UUID] = mapped_column(
        ForeignKey("market_response.id", ondelete="CASCADE"), index=True, unique=True
    )
    report_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("report.id", ondelete="SET NULL"),
        index=True,
        unique=True,
        server_default=text("NULL"),
    )
    status: Mapped[MarketDealStatus] = mapped_column(
        default=MarketDealStatus.IN_PROGRESS
    )

    market_response: Mapped[MarketResponse] = relationship(back_populates="market_deal")
    report: Mapped[Report | None] = relationship()


class MarketDealLoadEnum(StrEnum):
    MARKET_RESPONSE = "market_response"
    REPORT = "report"


class MarketDealDAO(BaseDAO[MarketDeal, UUID, MarketDealLoadEnum]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, MarketDeal)

    @property
    @override
    def _load_mapper(
        self,
    ) -> dict[MarketDealLoadEnum, ORMOption | Sequence[ORMOption]]:
        return {
            MarketDealLoadEnum.MARKET_RESPONSE: joinedload(MarketDeal.market_response),
            MarketDealLoadEnum.REPORT: joinedload(MarketDeal.report),
        }

    async def create(
        self,
        market_response_id: UUID,
        report_id: UUID | None = None,
    ) -> MarketDeal:
        obj = MarketDeal(
            market_response_id=market_response_id,
            report_id=report_id,
        )
        await self.save(obj)
        return obj


class MarketDealDAOFactory(BaseDAOFactory[MarketDealDAO]):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_maker, MarketDealDAO)
