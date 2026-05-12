from uuid import UUID

from teampass.domain_core import (
    DomainConflictException,
    DomainNotFoundException,
)


class GameCycleNotFoundException(DomainNotFoundException):
    def __init__(self, cycle_id: UUID) -> None:
        self.cycle_id: UUID = cycle_id
        super().__init__(f"Game cycle with ID {cycle_id} not found")


class GameCycleOverlapException(DomainConflictException):
    def __init__(self, cycle_id: UUID) -> None:
        self.cycle_id: UUID = cycle_id
        super().__init__(f"Game cycle dates overlap with existing cycle {cycle_id}")


class NoActiveGameCycleException(DomainNotFoundException):
    def __init__(self) -> None:
        super().__init__("No active game cycle found")
