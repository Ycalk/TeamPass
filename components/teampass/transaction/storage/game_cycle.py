from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, override
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from sqlalchemy.orm.interfaces import ORMOption
from sqlalchemy.types import TIMESTAMP
from teampass.database import BaseDAO, BaseDAOFactory, BaseModel

if TYPE_CHECKING:
    from .cycle_snapshot import CycleSnapshot
    from .point_transaction import PointTransaction


class GameCycle(BaseModel):
    __tablename__: str = "game_cycle"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    start_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    end_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    point_transactions: Mapped[list[PointTransaction]] = relationship(
        back_populates="game_cycle", cascade="all, delete-orphan", passive_deletes=True
    )
    snapshots: Mapped[list[CycleSnapshot]] = relationship(
        back_populates="game_cycle", cascade="all, delete-orphan", passive_deletes=True
    )


class GameCycleLoadEnum(StrEnum):
    POINT_TRANSACTIONS = "point_transactions"


class GameCycleDAO(BaseDAO[GameCycle, UUID, GameCycleLoadEnum]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, GameCycle)

    @property
    @override
    def _load_mapper(self) -> dict[GameCycleLoadEnum, ORMOption | Sequence[ORMOption]]:
        return {
            GameCycleLoadEnum.POINT_TRANSACTIONS: selectinload(
                GameCycle.point_transactions
            )
        }

    async def create(self, start_date: datetime, end_date: datetime) -> GameCycle:
        obj = GameCycle(start_date=start_date, end_date=end_date)
        await self.save(obj)
        return obj


class GameCycleDAOFactory(BaseDAOFactory[GameCycleDAO]):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_maker, GameCycleDAO)
