from datetime import datetime, timezone
from typing import Final, override

import structlog
from opentelemetry import trace
from teampass.domain_core import DomainMethod
from teampass.transaction.dto import GameCycle
from teampass.transaction.storage import GameCycleDAO

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class GetCurrentCycleMethod(DomainMethod[None, GameCycle | None]):
    def __init__(
        self,
        game_cycle_dao: GameCycleDAO,
    ) -> None:
        self.game_cycle_dao: GameCycleDAO = game_cycle_dao

    @override
    async def __call__(self, command: None) -> GameCycle | None:
        with _tracer.start_as_current_span("transaction.get_current_cycle"):
            logger = _logger.bind()

            logger.info("fetching_current_game_cycle")

            now = datetime.now(timezone.utc)
            cycle = await self.game_cycle_dao.find_overlapping(now, now)

            if cycle is None:
                logger.info("no_active_game_cycle")
                return None

            logger.info("current_game_cycle_found", cycle_id=str(cycle.id))
            return GameCycle.from_persistent(cycle)
