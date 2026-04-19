from typing import Final, override
from uuid import UUID

import structlog
from opentelemetry import trace
from pydantic import BaseModel
from teampass.domain_core import DomainMethod
from teampass.team.dto import TeamInvitation
from teampass.team.storage import TeamInvitationDAO, TeamInvitationLoadEnum
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import UserDAO

from .exceptions import (
    InvitationAlreadyExistsException,
    UserAlreadyInTeamException,
    UserNotCaptainException,
    UserNotInTeamException,
)

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class InviteToTeamPayload(BaseModel):
    invited_user_id: UUID


class InviteToTeamCommand(InviteToTeamPayload):
    user_id: UUID


class InviteToTeamMethod(DomainMethod[InviteToTeamCommand, TeamInvitation]):
    def __init__(
        self,
        invitation_dao: TeamInvitationDAO,
        user_dao: UserDAO,
    ) -> None:
        self.invitation_dao: TeamInvitationDAO = invitation_dao
        self.user_dao: UserDAO = user_dao

    @override
    async def __call__(self, command: InviteToTeamCommand) -> TeamInvitation:
        with _tracer.start_as_current_span("team.invite") as span:
            span.set_attribute("inviter.id", str(command.user_id))
            span.set_attribute("invited_user.id", str(command.invited_user_id))
            logger = _logger.bind(
                inviter_id=str(command.user_id),
                invited_user_id=str(command.invited_user_id),
            )

            logger.info("inviting_user_to_team")

            inviter = await self.user_dao.find_by_id(command.user_id)
            if inviter is None:
                logger.error("inviter_not_found")
                raise UserNotFoundException(command.user_id)

            if inviter.team_id is None:
                logger.error("inviter_has_no_team")
                raise UserNotInTeamException(command.user_id)

            if not inviter.is_captain:
                span.set_attribute("inviter.team_id", str(inviter.team_id))
                logger.error("inviter_is_not_captain")
                raise UserNotCaptainException(command.user_id)

            invited_user = await self.user_dao.find_by_id(command.invited_user_id)
            if invited_user is None:
                logger.error("invited_user_not_found")
                raise UserNotFoundException(command.invited_user_id)

            if invited_user.team_id is not None:
                span.set_attribute("invited_user.team_id", str(invited_user.team_id))
                logger.error("invited_user_already_in_team")
                raise UserAlreadyInTeamException(command.invited_user_id)

            existing = await self.invitation_dao.find_by_user_and_team(
                user_id=command.invited_user_id,
                team_id=inviter.team_id,
            )
            if existing is not None:
                span.set_attribute("invitation.id", str(existing.id))
                logger.error("invitation_already_exists")
                raise InvitationAlreadyExistsException(
                    command.invited_user_id, inviter.team_id
                )

            invitation = await self.invitation_dao.create(
                user_id=command.invited_user_id,
                team_id=inviter.team_id,
            )
            await self.invitation_dao.commit()

            logger.info("invitation_created", invitation_id=str(invitation.id))
            fully_loaded_invitation = await self.invitation_dao.find_by_id(
                id=invitation.id,
                includes=[
                    TeamInvitationLoadEnum.USER,
                    TeamInvitationLoadEnum.TEAM_WITH_MEMBERS,
                ],
            )
            if fully_loaded_invitation is None:
                logger.error("invitation_not_found_after_creation")
                raise ValueError("Critical error: Invitation not found after creation")

            return TeamInvitation.from_persistent(fully_loaded_invitation)
