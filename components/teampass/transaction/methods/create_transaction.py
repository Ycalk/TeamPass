from typing import Final, override
from uuid import UUID

import structlog
from opentelemetry import trace
from pydantic import BaseModel, model_validator
from teampass.domain_core import DomainMethod
from teampass.transaction.dto import PointTransaction
from teampass.transaction.storage import (
    PointTransactionDAO,
    PointType,
)

from .exceptions import NoActiveGameCycleException
from .get_current_cycle import GetCurrentCycleMethod

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class CreateTransactionCommand(BaseModel):
    team_id: UUID | None = None
    user_id: UUID | None = None
    points: int
    points_type: PointType

    @model_validator(mode="after")
    def check_owner_xor(self) -> "CreateTransactionCommand":
        if (self.team_id is None) == (self.user_id is None):
            raise ValueError("Provide exactly one of team_id or user_id")
        return self


class CreateTransactionMethod(DomainMethod[CreateTransactionCommand, PointTransaction]):
    def __init__(
        self,
        point_transaction_dao: PointTransactionDAO,
        get_current_cycle: GetCurrentCycleMethod,
    ) -> None:
        self.point_transaction_dao: PointTransactionDAO = point_transaction_dao
        self.get_current_cycle: GetCurrentCycleMethod = get_current_cycle

    @override
    async def __call__(self, command: CreateTransactionCommand) -> PointTransaction:
        with _tracer.start_as_current_span("transaction.create_transaction") as span:
            span.set_attribute("transaction.points", command.points)
            span.set_attribute("transaction.points_type", command.points_type)
            logger = _logger.bind(
                team_id=str(command.team_id) if command.team_id else None,
                user_id=str(command.user_id) if command.user_id else None,
                points=command.points,
                points_type=command.points_type,
            )

            logger.info("creating_point_transaction")
            cycle = await self.get_current_cycle(None)
            if cycle is None:
                raise NoActiveGameCycleException()

            span.set_attribute("cycle.id", str(cycle.id))

            transaction = await self.point_transaction_dao.create(
                points=command.points,
                points_type=command.points_type,
                cycle_id=cycle.id,
                team_id=command.team_id,
                user_id=command.user_id,
            )
            await self.point_transaction_dao.commit()

            span.set_attribute("transaction.id", str(transaction.id))
            logger.info("point_transaction_created", transaction_id=str(transaction.id))

            return PointTransaction.from_persistent(transaction)
