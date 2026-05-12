from datetime import datetime
from typing import Final, override

import structlog
from opentelemetry import trace
from pydantic import BaseModel
from teampass.domain_core import DomainMethod
from teampass.transaction.dto import GameCycle
from teampass.transaction.storage import GameCycleDAO

from .exceptions import GameCycleOverlapException

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class CreateCycleCommand(BaseModel):
    start_date: datetime
    end_date: datetime


class CreateCycleMethod(DomainMethod[CreateCycleCommand, GameCycle]):
    def __init__(
        self,
        game_cycle_dao: GameCycleDAO,
    ) -> None:
        self.game_cycle_dao: GameCycleDAO = game_cycle_dao

    @override
    async def __call__(self, command: CreateCycleCommand) -> GameCycle:
        with _tracer.start_as_current_span("transaction.create_cycle") as span:
            span.set_attribute("cycle.start_date", command.start_date.isoformat())
            span.set_attribute("cycle.end_date", command.end_date.isoformat())
            logger = _logger.bind(
                start_date=command.start_date.isoformat(),
                end_date=command.end_date.isoformat(),
            )

            logger.info("creating_game_cycle")

            overlapping = await self.game_cycle_dao.find_overlapping(
                start_date=command.start_date,
                end_date=command.end_date,
            )

            if overlapping is not None:
                logger.error(
                    "game_cycle_overlap",
                    overlapping_id=str(overlapping.id),
                )
                raise GameCycleOverlapException(overlapping.id)

            cycle = await self.game_cycle_dao.create(
                start_date=command.start_date,
                end_date=command.end_date,
            )
            await self.game_cycle_dao.commit()

            span.set_attribute("cycle.id", str(cycle.id))
            logger.info("game_cycle_created", cycle_id=str(cycle.id))

            return GameCycle.from_persistent(cycle)
