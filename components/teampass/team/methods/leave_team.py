from typing import Final, override
from uuid import UUID

import structlog
from opentelemetry import trace
from pydantic import BaseModel
from teampass.domain_core import DomainMethod
from teampass.team.policies import TeamPolicies
from teampass.team.storage import TeamDAO, TeamLoadEnum
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import UserDAO

from .exceptions import (
    CaptainCannotLeaveTeamException,
    TeamTransfersDisabledException,
    UserNotInTeamException,
)

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class LeaveTeamCommand(BaseModel):
    user_id: UUID


class LeaveTeamMethod(DomainMethod[LeaveTeamCommand, None]):
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
    async def __call__(self, command: LeaveTeamCommand) -> None:
        with _tracer.start_as_current_span("team.leave") as span:
            span.set_attribute("user.id", str(command.user_id))
            logger = _logger.bind(user_id=str(command.user_id))

            logger.info("leaving_team")

            user = await self.user_dao.find_by_id(command.user_id)
            if user is None:
                logger.error("user_not_found")
                raise UserNotFoundException(command.user_id)

            if user.team_id is None:
                logger.error("user_not_in_team")
                raise UserNotInTeamException(command.user_id)

            team_id = user.team_id
            span.set_attribute("team.id", str(team_id))

            if not self.policies.allow_team_transfers:
                logger.error("transfers_disabled")
                raise TeamTransfersDisabledException()

            if user.is_captain:
                team = await self.team_dao.find_by_id(
                    id=team_id,
                    includes=[TeamLoadEnum.MEMBERS],
                )
                if team is None:
                    raise ValueError(
                        f"Critical error: Team {team_id} "
                        + f"not found for user {command.user_id}"
                    )

                other_members = [m for m in team.members if m.id != command.user_id]
                if len(other_members) > 0:
                    span.set_attribute("team.member_count", len(team.members))
                    logger.error("captain_cannot_leave_with_members")
                    raise CaptainCannotLeaveTeamException(command.user_id)

                user.team_id = None
                user.is_captain = False
                await self.user_dao.save(user)
                await self.team_dao.commit()

                logger.info("team_dissolved", team_id=str(team_id))
            else:
                user.team_id = None
                await self.user_dao.save(user)
                await self.user_dao.commit()

                logger.info("left_team", team_id=str(team_id))
