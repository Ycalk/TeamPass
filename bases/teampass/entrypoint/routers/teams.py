from typing import Final
from uuid import UUID

import structlog
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, status
from opentelemetry import trace
from teampass.entrypoint.exceptions import CustomHTTPException
from teampass.entrypoint.scheme import ErrorResponse
from teampass.entrypoint.security import get_current_user_id
from teampass.team import (
    AcceptInvitationCommand,
    AcceptInvitationMethod,
    CreateTeamCommand,
    CreateTeamMethod,
    CreateTeamPayload,
    DeleteInvitationCommand,
    DeleteInvitationMethod,
    InviteToTeamCommand,
    InviteToTeamMethod,
    InviteToTeamPayload,
    LeaveTeamCommand,
    LeaveTeamMethod,
    RemoveTeamMemberCommand,
    RemoveTeamMemberMethod,
    RenameTeamCommand,
    RenameTeamMethod,
    RenameTeamPayload,
    TransferCaptaincyCommand,
    TransferCaptaincyMethod,
    TransferCaptaincyPayload,
)
from teampass.team.dto import Team, TeamInvitation
from teampass.team.storage import (
    TeamDAO,
    TeamInvitationDAO,
    TeamInvitationLoadEnum,
    TeamLoadEnum,
)

_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Не валидный access токен",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Ресурс не найден",
        },
    },
    route_class=DishkaRoute,
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "Пользователь уже состоит в команде",
        },
    },
)
async def create_team(
    method: FromDishka[CreateTeamMethod],
    payload: CreateTeamPayload,
    user_id: UUID = Depends(get_current_user_id),
) -> Team:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    span.set_attribute("team.name", payload.name)
    logger = _logger.bind(user_id=str(user_id), team_name=payload.name)
    logger.info("processing_create_team_request")

    res = await method(CreateTeamCommand(user_id=user_id, **payload.model_dump()))
    logger.info("create_team_request_processed")
    return res


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_my_team(
    team_dao: FromDishka[TeamDAO],
    user_id: UUID = Depends(get_current_user_id),
) -> Team:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    logger = _logger.bind(user_id=str(user_id))
    logger.info("processing_get_my_team_request")

    team = await team_dao.find_by_user_id(user_id, includes=[TeamLoadEnum.MEMBERS])
    if team is None:
        logger.error("team_not_found")
        raise CustomHTTPException(
            error="TeamNotFound",
            message="Team not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    span.set_attribute("team.id", str(team.id))
    logger.info("get_my_team_request_processed")
    return Team.from_persistent(team)


@router.get("/{team_id}", status_code=status.HTTP_200_OK)
async def get_team(
    team_dao: FromDishka[TeamDAO],
    team_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
) -> Team:
    span = trace.get_current_span()
    span.set_attribute("team.id", str(team_id))
    span.set_attribute("user.id", str(user_id))
    logger = _logger.bind(team_id=str(team_id), user_id=str(user_id))
    logger.info("processing_get_team_request")

    team = await team_dao.find_by_id(team_id, includes=[TeamLoadEnum.MEMBERS])
    if team is None:
        logger.error("team_not_found")
        raise CustomHTTPException(
            error="TeamNotFound",
            message="Team not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    span.set_attribute("team.id", str(team.id))
    logger.info("get_my_team_request_processed")
    return Team.from_persistent(team)


@router.patch(
    "/me/name",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": (
                "Пользователь не является капитаном команды "
                + "или не состоит в команде"
            ),
        },
    },
)
async def change_my_team_name(
    method: FromDishka[RenameTeamMethod],
    payload: RenameTeamPayload,
    user_id: UUID = Depends(get_current_user_id),
) -> Team:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    span.set_attribute("team.new_name", payload.name)
    logger = _logger.bind(user_id=str(user_id), team_new_name=payload.name)
    logger.info("processing_change_my_team_name_request")

    res = await method(RenameTeamCommand(user_id=user_id, **payload.model_dump()))
    logger.info("change_my_team_name_request_processed")
    return res


@router.patch(
    "/me/captaincy",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": (
                "Пользователь не является капитаном команды "
                + "/ не состоит в команде / пользователи в разных командах"
            ),
        },
    },
)
async def transfer_captaincy(
    method: FromDishka[TransferCaptaincyMethod],
    payload: TransferCaptaincyPayload,
    user_id: UUID = Depends(get_current_user_id),
) -> Team:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    span.set_attribute("team.new_captain_id", str(payload.new_captain_id))
    logger = _logger.bind(
        user_id=str(user_id), team_new_captain_id=str(payload.new_captain_id)
    )
    logger.info("processing_transfer_captaincy_request")

    res = await method(
        TransferCaptaincyCommand(user_id=user_id, **payload.model_dump())
    )
    logger.info("transfer_captaincy_request_processed")
    return res


@router.post(
    "/me/invitations",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": (
                "Пользователь не является капитаном команды "
                + "или не состоит в команде"
            ),
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": (
                "Пользователь уже состоит в команде "
                + "или такое приглашение уже существует"
            ),
        },
    },
)
async def invite_to_team(
    method: FromDishka[InviteToTeamMethod],
    payload: InviteToTeamPayload,
    user_id: UUID = Depends(get_current_user_id),
) -> TeamInvitation:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    span.set_attribute("team.invited_user_id", str(payload.invited_user_id))
    logger = _logger.bind(
        user_id=str(user_id), team_invited_user_id=str(payload.invited_user_id)
    )
    logger.info("processing_invite_to_team_request")

    res = await method(InviteToTeamCommand(user_id=user_id, **payload.model_dump()))
    logger.info("invite_to_team_request_processed")
    return res


@router.get(
    "/me/invitations",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "Пользователь не является капитаном команды",
        },
    },
)
async def get_team_invitations(
    team_invitation_dao: FromDishka[TeamInvitationDAO],
    team_dao: FromDishka[TeamDAO],
    user_id: UUID = Depends(get_current_user_id),
) -> list[TeamInvitation]:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    logger = _logger.bind(user_id=str(user_id))
    logger.info("processing_get_team_invitations_request")

    team = await team_dao.find_by_user_id(user_id, includes=[TeamLoadEnum.MEMBERS])
    if team is None:
        logger.error("team_not_found")
        raise CustomHTTPException(
            error="TeamNotFoundException",
            message="Team not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    span.set_attribute("team.id", str(team.id))
    if team.captain is None or team.captain.id != user_id:
        logger.error("not_team_captain")
        raise CustomHTTPException(
            error="UserNotCaptainException",
            message="You are not a team captain",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    invitations = await team_invitation_dao.find_by_team_id(
        team.id, includes=[TeamInvitationLoadEnum.TEAM_WITH_MEMBERS]
    )
    logger.info("get_team_invitations_request_processed")
    return [TeamInvitation.from_persistent(invitation) for invitation in invitations]


@router.delete(
    "/invitations/{invitation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": (
                "Запрещено удалять приглашение. "
                + "Приглашение может удалить только его получатель "
                + "или капитан команды, отправивший приглашение"
            ),
        },
    },
)
async def delete_invitation(
    method: FromDishka[DeleteInvitationMethod],
    invitation_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
):
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    span.set_attribute("invitation.id", str(invitation_id))
    logger = _logger.bind(user_id=str(user_id), invitation_id=str(invitation_id))
    logger.info("processing_delete_invitation_request")

    await method(DeleteInvitationCommand(user_id=user_id, invitation_id=invitation_id))
    logger.info("delete_invitation_request_processed")


@router.post(
    "/invitations/{invitation_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "Пользователь уже состоит в команде",
        },
    },
)
async def accept_invitation(
    method: FromDishka[AcceptInvitationMethod],
    invitation_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
) -> TeamInvitation:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    span.set_attribute("invitation.id", str(invitation_id))
    logger = _logger.bind(user_id=str(user_id), invitation_id=str(invitation_id))
    logger.info("processing_accept_invitation_request")

    res = await method(
        AcceptInvitationCommand(user_id=user_id, invitation_id=invitation_id)
    )
    logger.info("accept_invitation_request_processed")
    return res


@router.get("/invitations", status_code=status.HTTP_200_OK)
async def get_user_invitations(
    invitation_dao: FromDishka[TeamInvitationDAO],
    user_id: UUID = Depends(get_current_user_id),
) -> list[TeamInvitation]:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    logger = _logger.bind(user_id=str(user_id))
    logger.info("processing_get_user_invitations_request")

    invitations = await invitation_dao.find_by_user_id(
        user_id, includes=[TeamInvitationLoadEnum.TEAM_WITH_MEMBERS]
    )
    logger.info("get_user_invitations_request_processed")
    return [TeamInvitation.from_persistent(invitation) for invitation in invitations]


@router.delete(
    "/me/members/{member_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": (
                "Пользователь не является капитаном команды "
                + "/ не состоит в команде / пользователи в разных командах "
                + "/ капитан пытается удалить себя"
            ),
        },
    },
)
async def remove_team_member(
    method: FromDishka[RemoveTeamMemberMethod],
    member_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
) -> Team:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    span.set_attribute("team.member_id", str(member_id))
    logger = _logger.bind(user_id=str(user_id), team_member_id=str(member_id))
    logger.info("processing_remove_team_member_request")

    res = await method(
        RemoveTeamMemberCommand(user_id=user_id, target_user_id=member_id)
    )
    logger.info("remove_team_member_request_processed")
    return res


@router.delete(
    "/me/members/me",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": (
                "Пользователь не состоит в команде "
                + "/ капитан не может выйти из команды с участниками"
            ),
        },
    },
)
async def leave_team(
    method: FromDishka[LeaveTeamMethod],
    user_id: UUID = Depends(get_current_user_id),
):
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    logger = _logger.bind(user_id=str(user_id))
    logger.info("processing_leave_team_request")

    await method(LeaveTeamCommand(user_id=user_id))
    logger.info("leave_team_request_processed")
