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
    InvitationAlreadyAcceptedException,
    InvitationDeleteForbiddenException,
    InvitationNotFoundException,
)

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class DeleteInvitationPayload(BaseModel):
    invitation_id: UUID


class DeleteInvitationCommand(DeleteInvitationPayload):
    user_id: UUID


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
            span.set_attribute("initiator.id", str(command.user_id))
            span.set_attribute("invitation.id", str(command.invitation_id))
            logger = _logger.bind(
                initiator_id=str(command.user_id),
                invitation_id=str(command.invitation_id),
            )

            logger.info("deleting_invitation")

            invitation = await self.invitation_dao.find_by_id(command.invitation_id)
            if invitation is None:
                logger.error("invitation_not_found")
                raise InvitationNotFoundException(command.invitation_id)

            initiator = await self.user_dao.find_by_id(command.user_id)
            if initiator is None:
                logger.error("initiator_not_found")
                raise UserNotFoundException(command.user_id)

            is_invited_user = initiator.id == invitation.user_id
            is_team_captain = (
                initiator.is_captain and initiator.team_id == invitation.team_id
            )

            if not (is_invited_user or is_team_captain):
                span.set_attribute("invitation.team_id", str(invitation.team_id))
                span.set_attribute("invitation.user_id", str(invitation.user_id))
                logger.error("initiator_not_authorized_to_delete_invitation")
                raise InvitationDeleteForbiddenException(
                    command.user_id, command.invitation_id
                )

            if invitation.accepted_at is not None:
                logger.error("invitation_already_accepted")
                span.set_attribute(
                    "invitation.accepted_at", str(invitation.accepted_at)
                )
                raise InvitationAlreadyAcceptedException(command.invitation_id)

            await self.invitation_dao.delete(invitation)
            await self.invitation_dao.commit()

            logger.info("invitation_deleted")
