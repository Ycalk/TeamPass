from typing import Final, override
from uuid import UUID

import structlog
from opentelemetry import trace
from pydantic import BaseModel
from teampass.domain_core import DomainMethod
from teampass.team.storage import TeamInvitationDAO
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import UserDAO

from .exceptions import (
    InvitationDeleteForbiddenException,
    InvitationNotFoundException,
)

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class DeleteInvitationPayload(BaseModel):
    invitation_id: UUID


class DeleteInvitationCommand(DeleteInvitationPayload):
    initiator_id: UUID


class DeleteInvitationMethod(DomainMethod[DeleteInvitationCommand, None]):
    def __init__(
        self,
        invitation_dao: TeamInvitationDAO,
        user_dao: UserDAO,
    ) -> None:
        self.invitation_dao: TeamInvitationDAO = invitation_dao
        self.user_dao: UserDAO = user_dao

    @override
    async def __call__(self, command: DeleteInvitationCommand) -> None:
        with _tracer.start_as_current_span("team.delete_invitation") as span:
            span.set_attribute("initiator.id", str(command.initiator_id))
            span.set_attribute("invitation.id", str(command.invitation_id))
            logger = _logger.bind(
                initiator_id=str(command.initiator_id),
                invitation_id=str(command.invitation_id),
            )

            logger.info("deleting_invitation")

            invitation = await self.invitation_dao.find_by_id(command.invitation_id)
            if invitation is None:
                logger.error("invitation_not_found")
                raise InvitationNotFoundException(command.invitation_id)

            initiator = await self.user_dao.find_by_id(command.initiator_id)
            if initiator is None:
                logger.error("initiator_not_found")
                raise UserNotFoundException(command.initiator_id)

            is_invited_user = initiator.id == invitation.user_id
            is_team_captain = (
                initiator.is_captain and initiator.team_id == invitation.team_id
            )

            if not (is_invited_user or is_team_captain):
                span.set_attribute("invitation.team_id", str(invitation.team_id))
                span.set_attribute("invitation.user_id", str(invitation.user_id))
                logger.error("initiator_not_authorized_to_delete_invitation")
                raise InvitationDeleteForbiddenException(
                    command.initiator_id, command.invitation_id
                )

            await self.invitation_dao.delete(invitation)
            await self.invitation_dao.commit()

            logger.info("invitation_deleted")
