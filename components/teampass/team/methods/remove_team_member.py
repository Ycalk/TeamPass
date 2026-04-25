from typing import Final, override
from uuid import UUID

import structlog
from opentelemetry import trace
from pydantic import BaseModel
from teampass.domain_core import DomainMethod
from teampass.team.dto import Team
from teampass.team.policies import TeamPolicies
from teampass.team.storage import TeamDAO, TeamLoadEnum
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import UserDAO

from .exceptions import (
    CaptainCannotRemoveSelfException,
    TeamTransfersDisabledException,
    UserNotCaptainException,
    UserNotInTeamException,
    UsersNotInSameTeamException,
)

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class RemoveTeamMemberPayload(BaseModel):
    target_user_id: UUID


class RemoveTeamMemberCommand(RemoveTeamMemberPayload):
    user_id: UUID


class RemoveTeamMemberMethod(DomainMethod[RemoveTeamMemberCommand, Team]):
    def __init__(
        self,
        team_dao: TeamDAO,
        user_dao: UserDAO,
        policies: TeamPolicies,
    ) -> None:
        self.team_dao: TeamDAO = team_dao
        self.user_dao: UserDAO = user_dao
        self.policies: TeamPolicies = policies

    @override
    async def __call__(self, command: RemoveTeamMemberCommand) -> Team:
        with _tracer.start_as_current_span("team.remove_member") as span:
            span.set_attribute("initiator.id", str(command.user_id))
            span.set_attribute("target_user.id", str(command.target_user_id))
            logger = _logger.bind(
                initiator_id=str(command.user_id),
                target_user_id=str(command.target_user_id),
            )

            logger.info("removing_team_member")

            initiator = await self.user_dao.find_by_id(command.user_id)
            if initiator is None:
                logger.error("initiator_not_found")
                raise UserNotFoundException(command.user_id)

            if initiator.team_id is None:
                logger.error("initiator_has_no_team")
                raise UserNotInTeamException(command.user_id)

            if not initiator.is_captain:
                span.set_attribute("initiator.team_id", str(initiator.team_id))
                logger.error("initiator_is_not_captain")
                raise UserNotCaptainException(command.user_id)

            if command.user_id == command.target_user_id:
                logger.error("captain_cannot_remove_self")
                raise CaptainCannotRemoveSelfException(command.user_id)

            target_user = await self.user_dao.find_by_id(command.target_user_id)
            if target_user is None:
                logger.error("target_user_not_found")
                raise UserNotFoundException(command.target_user_id)

            if target_user.team_id != initiator.team_id:
                span.set_attribute("target_user.team_id", str(target_user.team_id))
                logger.error("target_user_not_in_same_team")
                raise UsersNotInSameTeamException(command.target_user_id)

            if not self.policies.allow_team_transfers:
                logger.error("transfers_disabled")
                raise TeamTransfersDisabledException()

            team_id = initiator.team_id
            target_user.team_id = None

            await self.user_dao.save(target_user)
            await self.user_dao.commit()

            logger.info("team_member_removed", team_id=str(team_id))

            fully_loaded_team = await self.team_dao.find_by_id(
                id=team_id,
                includes=[TeamLoadEnum.MEMBERS],
            )
            if fully_loaded_team is None:
                raise ValueError("Critical error: Team not found after member removal")

            return Team.from_persistent(fully_loaded_team)
