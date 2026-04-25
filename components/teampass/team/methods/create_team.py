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
from teampass.user.storage import UserDAO, UserLoadEnum

from .exceptions import TeamTransfersDisabledException, UserAlreadyInTeamException

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class CreateTeamPayload(BaseModel):
    name: str


class CreateTeamCommand(CreateTeamPayload):
    user_id: UUID


class CreateTeamMethod(DomainMethod[CreateTeamCommand, Team]):
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
    async def __call__(self, command: CreateTeamCommand) -> Team:
        with _tracer.start_as_current_span("team.create") as span:
            span.set_attribute("user.id", str(command.user_id))
            span.set_attribute("team.name", command.name)
            logger = _logger.bind(
                user_id=str(command.user_id),
                team_name=command.name,
            )

            logger.info("creating_team")

            user = await self.user_dao.find_by_id(
                command.user_id, includes=[UserLoadEnum.STUDENT]
            )
            if user is None:
                logger.error("user_not_found")
                raise UserNotFoundException(command.user_id)

            if user.team_id is not None:
                span.set_attribute("team.existing_team.id", str(user.team_id))
                logger.error("user_already_in_team")
                raise UserAlreadyInTeamException(command.user_id)

            if not self.policies.allow_team_transfers:
                logger.error("transfers_disabled")
                raise TeamTransfersDisabledException()

            team = await self.team_dao.create(command.name)
            user.team_id = team.id
            user.is_captain = True
            await self.user_dao.save(user)
            await self.user_dao.commit()

            logger.info("team_created")
            fully_loaded_team = await self.team_dao.find_by_id(
                id=team.id, includes=[TeamLoadEnum.MEMBERS]
            )
            if fully_loaded_team is None:
                raise ValueError("Critical error: Team not found after creation")

            return Team.from_persistent(fully_loaded_team)
