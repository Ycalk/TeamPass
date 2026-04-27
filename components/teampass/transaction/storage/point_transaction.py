from __future__ import annotations

from collections.abc import Sequence
from enum import StrEnum
from typing import TYPE_CHECKING, Any, overload, override
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, joinedload, mapped_column, relationship
from sqlalchemy.orm.interfaces import ORMOption
from teampass.database import BaseDAO, BaseDAOFactory, BaseModel

if TYPE_CHECKING:
    from teampass.team.storage import Team
    from teampass.user.storage import User

    from .game_cycle import GameCycle


class PointTransaction(BaseModel):
    __tablename__: str = "point_transaction"
    __table_args__: tuple[Any, ...] = (
        CheckConstraint(
            "(team_id IS NULL) != (user_id IS NULL)",
            name="check_point_transaction_owner_xor",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    cycle_id: Mapped[UUID] = mapped_column(
        ForeignKey("game_cycle.id", ondelete="CASCADE"), index=True
    )
    team_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("team.id", ondelete="CASCADE"), index=True, server_default=None
    )
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), index=True, server_default=None
    )
    points: Mapped[int] = mapped_column()

    user: Mapped[User | None] = relationship(back_populates="point_transactions")
    team: Mapped[Team | None] = relationship(back_populates="point_transactions")
    game_cycle: Mapped[GameCycle] = relationship(back_populates="point_transactions")


class PointTransactionLoadEnum(StrEnum):
    RECIPIENT = "recipient"
    GAME_CYCLE = "game_cycle"


class PointTransactionDAO(BaseDAO[PointTransaction, UUID, PointTransactionLoadEnum]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, PointTransaction)

    @property
    @override
    def _load_mapper(
        self,
    ) -> dict[PointTransactionLoadEnum, ORMOption | Sequence[ORMOption]]:
        return {
            PointTransactionLoadEnum.RECIPIENT: [
                joinedload(PointTransaction.user),
                joinedload(PointTransaction.team),
            ],
            PointTransactionLoadEnum.GAME_CYCLE: joinedload(
                PointTransaction.game_cycle
            ),
        }

    @overload
    async def create(self, points: int, cycle_id: UUID, *, team_id: UUID): ...

    @overload
    async def create(self, points: int, cycle_id: UUID, *, user_id: UUID): ...

    async def create(
        self,
        points: int,
        cycle_id: UUID,
        *,
        team_id: UUID | None = None,
        user_id: UUID | None = None,
    ) -> PointTransaction:
        if (team_id is None) ^ (user_id is None):
            raise ValueError("Provide exactly one of team_id or user_id")
        obj = PointTransaction(
            points=points, cycle_id=cycle_id, team_id=team_id, user_id=user_id
        )
        await self.save(obj)
        return obj


class PointTransactionDAOFactory(BaseDAOFactory[PointTransactionDAO]):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_maker, PointTransactionDAO)
