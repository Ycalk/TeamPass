from datetime import datetime, timezone
from typing import Final, override
from uuid import UUID

import structlog
from opentelemetry import trace
from pydantic import BaseModel
from teampass.domain_core import DomainMethod
from teampass.team.dto import TeamInvitation
from teampass.team.storage import TeamInvitationDAO, TeamInvitationLoadEnum
from teampass.user.storage import UserDAO

from .exceptions import (
    InvitationNotFoundException,
    UserAlreadyInTeamException,
)

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class AcceptInvitationPayload(BaseModel):
    invitation_id: UUID


class AcceptInvitationCommand(AcceptInvitationPayload):
    user_id: UUID


class AcceptInvitationMethod(DomainMethod[AcceptInvitationCommand, TeamInvitation]):
    def __init__(
        self,
        invitation_dao: TeamInvitationDAO,
        user_dao: UserDAO,
    ) -> None:
        self.invitation_dao: TeamInvitationDAO = invitation_dao
        self.user_dao: UserDAO = user_dao

    @override
    async def __call__(self, command: AcceptInvitationCommand) -> TeamInvitation:
        with _tracer.start_as_current_span("team.accept_invitation") as span:
            span.set_attribute("user.id", str(command.user_id))
            span.set_attribute("invitation.id", str(command.invitation_id))
            logger = _logger.bind(
                user_id=str(command.user_id),
                invitation_id=str(command.invitation_id),
            )

            logger.info("accepting_invitation")

            invitation = await self.invitation_dao.find_by_id(command.invitation_id)
            if invitation is None:
                logger.error("invitation_not_found")
                raise InvitationNotFoundException(command.invitation_id)

            user = await self.user_dao.find_by_id(command.user_id)
            if user is None or user.id != invitation.user_id:
                logger.error("invitation_not_found")
                raise InvitationNotFoundException(command.invitation_id)

            if user.team_id is not None:
                span.set_attribute("user.team_id", str(user.team_id))
                logger.error("user_already_in_team")
                raise UserAlreadyInTeamException(command.user_id)

            invitation.accepted_at = datetime.now(timezone.utc)
            user.team_id = invitation.team_id

            await self.invitation_dao.save(invitation)
            await self.user_dao.save(user)
            await self.invitation_dao.commit()

            logger.info("invitation_accepted", team_id=str(invitation.team_id))

            fully_loaded_invitation = await self.invitation_dao.find_by_id(
                id=invitation.id,
                includes=[
                    TeamInvitationLoadEnum.USER,
                    TeamInvitationLoadEnum.TEAM_WITH_MEMBERS,
                ],
            )
            if fully_loaded_invitation is None:
                raise ValueError(
                    "Critical error: Invitation not found after acceptance"
                )

            return TeamInvitation.from_persistent(fully_loaded_invitation)
