from typing import Self
from uuid import UUID

from pydantic import BaseModel
from teampass.transaction.storage import PointTransaction as PointTransactionPersistence
from teampass.transaction.storage import PointType


class PointTransaction(BaseModel):
    id: UUID
    cycle_id: UUID
    team_id: UUID | None
    user_id: UUID | None
    points: int
    points_type: PointType

    @classmethod
    def from_persistent(cls, transaction: PointTransactionPersistence) -> Self:
        return cls(
            id=transaction.id,
            cycle_id=transaction.cycle_id,
            team_id=transaction.team_id,
            user_id=transaction.user_id,
            points=transaction.points,
            points_type=transaction.points_type,
        )
