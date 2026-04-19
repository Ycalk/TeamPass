from typing import Final, override
from uuid import UUID

import structlog
from opentelemetry import trace
from pydantic import BaseModel
from teampass.domain_core import DomainMethod
from teampass.team.dto import Team
from teampass.team.storage import TeamDAO, TeamLoadEnum
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import UserDAO

from .exceptions import (
    UserNotCaptainException,
    UserNotInTeamException,
)

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class RenameTeamPayload(BaseModel):
    name: str


class RenameTeamCommand(RenameTeamPayload):
    initiator_id: UUID


class RenameTeamMethod(DomainMethod[RenameTeamCommand, Team]):
    def __init__(
        self,
        team_dao: TeamDAO,
        user_dao: UserDAO,
    ) -> None:
        self.team_dao: TeamDAO = team_dao
        self.user_dao: UserDAO = user_dao

    @override
    async def __call__(self, command: RenameTeamCommand) -> Team:
        with _tracer.start_as_current_span("team.rename") as span:
            span.set_attribute("initiator.id", str(command.initiator_id))
            span.set_attribute("team.new_name", command.name)
            logger = _logger.bind(
                initiator_id=str(command.initiator_id),
                new_name=command.name,
            )

            logger.info("renaming_team")

            initiator = await self.user_dao.find_by_id(command.initiator_id)
            if initiator is None:
                logger.error("initiator_not_found")
                raise UserNotFoundException(command.initiator_id)

            if initiator.team_id is None:
                logger.error("initiator_has_no_team")
                raise UserNotInTeamException(command.initiator_id)

            if not initiator.is_captain:
                span.set_attribute("initiator.team_id", str(initiator.team_id))
                logger.error("initiator_is_not_captain")
                raise UserNotCaptainException(command.initiator_id)

            team = await self.team_dao.find_by_id(initiator.team_id)
            if team is None:
                raise ValueError(f"Critical error: Team {initiator.team_id} not found")

            span.set_attribute("team.id", str(team.id))
            span.set_attribute("team.old_name", team.name)

            team.name = command.name
            await self.team_dao.save(team)
            await self.team_dao.commit()

            logger.info("team_renamed", team_id=str(team.id))

            fully_loaded_team = await self.team_dao.find_by_id(
                id=team.id,
                includes=[TeamLoadEnum.MEMBERS],
            )
            if fully_loaded_team is None:
                raise ValueError("Critical error: Team not found after rename")

            return Team.from_persistent(fully_loaded_team)
