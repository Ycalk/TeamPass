from decimal import Decimal
from typing import Self
from uuid import UUID

from pydantic import BaseModel
from teampass.transaction.storage import CycleSnapshot as CycleSnapshotPersistence
from teampass.transaction.storage import GameCycle as GameCyclePersistence


class GameCycle(BaseModel):
    id: UUID
    start_date: int
    end_date: int

    @classmethod
    def from_persistent(cls, game_cycle: GameCyclePersistence) -> Self:
        return cls(
            id=game_cycle.id,
            start_date=int(game_cycle.start_date.timestamp()),
            end_date=int(game_cycle.end_date.timestamp()),
        )


class CycleSnapshot(BaseModel):
    id: UUID
    cycle_id: UUID
    team_id: UUID | None
    user_id: UUID | None
    activity_score: Decimal
    bonus_score: Decimal
    total_score: Decimal

    @classmethod
    def from_persistent(cls, cycle_snapshot: CycleSnapshotPersistence) -> Self:
        return cls(
            id=cycle_snapshot.id,
            cycle_id=cycle_snapshot.cycle_id,
            team_id=cycle_snapshot.team_id,
            user_id=cycle_snapshot.user_id,
            activity_score=cycle_snapshot.activity_score,
            bonus_score=cycle_snapshot.bonus_score,
            total_score=cycle_snapshot.total_score,
        )
