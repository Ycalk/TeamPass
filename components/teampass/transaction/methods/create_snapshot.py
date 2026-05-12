from decimal import ROUND_HALF_UP, Decimal
from typing import Final, override
from uuid import UUID

import structlog
from opentelemetry import trace
from pydantic import BaseModel, model_validator
from teampass.domain_core import DomainMethod
from teampass.transaction.dto import CycleSnapshot
from teampass.transaction.policies import TransactionPolicies
from teampass.transaction.storage import (
    CycleSnapshotDAO,
    GameCycleDAO,
    PointTransactionDAO,
    PointType,
)

from .exceptions import GameCycleNotFoundException

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class CreateSnapshotCommand(BaseModel):
    cycle_id: UUID
    team_id: UUID | None = None
    user_id: UUID | None = None

    @model_validator(mode="after")
    def check_owner_xor(self) -> "CreateSnapshotCommand":
        if (self.team_id is None) == (self.user_id is None):
            raise ValueError("Provide exactly one of team_id or user_id")
        return self


class CreateSnapshotMethod(DomainMethod[CreateSnapshotCommand, CycleSnapshot]):
    def __init__(
        self,
        cycle_snapshot_dao: CycleSnapshotDAO,
        game_cycle_dao: GameCycleDAO,
        point_transaction_dao: PointTransactionDAO,
        policies: TransactionPolicies,
    ) -> None:
        self.cycle_snapshot_dao: CycleSnapshotDAO = cycle_snapshot_dao
        self.game_cycle_dao: GameCycleDAO = game_cycle_dao
        self.point_transaction_dao: PointTransactionDAO = point_transaction_dao
        self.policies: TransactionPolicies = policies

    @override
    async def __call__(self, command: CreateSnapshotCommand) -> CycleSnapshot:
        with _tracer.start_as_current_span("transaction.create_snapshot") as span:
            span.set_attribute("cycle.id", str(command.cycle_id))
            span.set_attribute("cycle.id", str(command.cycle_id))
            logger = _logger.bind(
                cycle_id=str(command.cycle_id),
                team_id=str(command.team_id) if command.team_id else None,
                user_id=str(command.user_id) if command.user_id else None,
            )

            logger.info("creating_cycle_snapshot")

            cycle = await self.game_cycle_dao.find_by_id(command.cycle_id)
            if cycle is None:
                logger.error("game_cycle_not_found")
                raise GameCycleNotFoundException(command.cycle_id)

            points_by_type = await self.point_transaction_dao.sum_points_by_type(
                cycle_id=command.cycle_id,
                team_id=command.team_id,
                user_id=command.user_id,
            )

            raw_activity = points_by_type.get(PointType.ACTIVITY, 0)
            raw_bonus = points_by_type.get(PointType.BONUS, 0)

            max_activity = self.policies.max_activity_points
            max_bonus = self.policies.max_bonus_points
            point_ration = self.policies.point_ration

            normalized_activity = (
                min(raw_activity / max_activity, 1.0) * 100 if max_activity > 0 else 0
            )
            normalized_bonus = (
                min(raw_bonus / max_bonus, 1.0) * 100 if max_bonus > 0 else 0
            )

            total_score = normalized_activity * point_ration + normalized_bonus * (
                1 - point_ration
            )
            quantize_pattern = Decimal("0.01")
            activity_decimal = Decimal(str(normalized_activity)).quantize(
                quantize_pattern, rounding=ROUND_HALF_UP
            )
            bonus_decimal = Decimal(str(normalized_bonus)).quantize(
                quantize_pattern, rounding=ROUND_HALF_UP
            )
            total_decimal = Decimal(str(total_score)).quantize(
                quantize_pattern, rounding=ROUND_HALF_UP
            )

            snapshot = (
                await self.cycle_snapshot_dao.find_by_cycle_id_and_team_id_or_user_id(
                    command.cycle_id, team_id=command.team_id, user_id=command.user_id
                )
            )

            if snapshot is None:
                snapshot = await self.cycle_snapshot_dao.create(
                    activity_score=activity_decimal,
                    bonus_score=bonus_decimal,
                    total_score=total_decimal,
                    cycle_id=command.cycle_id,
                    team_id=command.team_id,
                    user_id=command.user_id,
                )
            else:
                snapshot.activity_score = activity_decimal
                snapshot.bonus_score = bonus_decimal
                snapshot.total_score = total_decimal
                await self.cycle_snapshot_dao.save(snapshot)

            await self.cycle_snapshot_dao.commit()

            span.set_attribute("snapshot.id", str(snapshot.id))
            span.set_attribute("snapshot.activity_score", str(activity_decimal))
            span.set_attribute("snapshot.bonus_score", str(bonus_decimal))
            span.set_attribute("snapshot.total_score", str(total_decimal))

            logger.info(
                "cycle_snapshot_created",
                snapshot_id=str(snapshot.id),
                activity_score=str(activity_decimal),
                bonus_score=str(bonus_decimal),
                total_score=str(total_decimal),
            )

            return CycleSnapshot.from_persistent(snapshot)
