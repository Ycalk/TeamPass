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
    UsersNotInSameTeamException,
)

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class TransferCaptaincyPayload(BaseModel):
    new_captain_id: UUID


class TransferCaptaincyCommand(TransferCaptaincyPayload):
    initiator_id: UUID


class TransferCaptaincyMethod(DomainMethod[TransferCaptaincyCommand, Team]):
    def __init__(
        self,
        team_dao: TeamDAO,
        user_dao: UserDAO,
    ) -> None:
        self.team_dao: TeamDAO = team_dao
        self.user_dao: UserDAO = user_dao

    @override
    async def __call__(self, command: TransferCaptaincyCommand) -> Team:
        with _tracer.start_as_current_span("team.transfer_captaincy") as span:
            span.set_attribute("initiator.id", str(command.initiator_id))
            span.set_attribute("new_captain.id", str(command.new_captain_id))
            logger = _logger.bind(
                initiator_id=str(command.initiator_id),
                new_captain_id=str(command.new_captain_id),
            )

            logger.info("transferring_captaincy")

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

            new_captain = await self.user_dao.find_by_id(command.new_captain_id)
            if new_captain is None:
                logger.error("new_captain_not_found")
                raise UserNotFoundException(command.new_captain_id)

            if new_captain.team_id != initiator.team_id:
                span.set_attribute("new_captain.team_id", str(new_captain.team_id))
                logger.error("new_captain_not_in_same_team")
                raise UsersNotInSameTeamException(command.new_captain_id)

            initiator.is_captain = False
            await self.user_dao.save(initiator)

            new_captain.is_captain = True
            await self.user_dao.save(new_captain)
            await self.user_dao.commit()

            logger.info("captaincy_transferred", team_id=str(initiator.team_id))

            fully_loaded_team = await self.team_dao.find_by_id(
                id=initiator.team_id,
                includes=[TeamLoadEnum.MEMBERS],
            )
            if fully_loaded_team is None:
                raise ValueError(
                    "Critical error: Team not found after captaincy transfer"
                )

            return Team.from_persistent(fully_loaded_team)
