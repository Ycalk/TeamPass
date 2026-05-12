import json
from collections.abc import Sequence
from typing import Any, ClassVar, override
from uuid import UUID

from dishka.integrations.starlette import FromDishka
from sqladmin import ModelView, expose
from sqladmin._types import MODEL_ATTR
from sqlalchemy import Column, Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from teampass.admin_panel.formatters import (
    created_at_formatter,
    updated_at_formatter,
)
from teampass.admin_panel.inject import INJECT, inject_from_request
from teampass.team.methods.accept_invitation import (
    AcceptInvitationCommand,
    AcceptInvitationMethod,
)
from teampass.team.methods.invite_to_team import InviteToTeamCommand, InviteToTeamMethod
from teampass.team.methods.leave_team import LeaveTeamCommand, LeaveTeamMethod
from teampass.team.methods.transfer_captaincy import (
    TransferCaptaincyCommand,
    TransferCaptaincyMethod,
)
from teampass.team.storage import Team as TeamModel
from teampass.team.storage import TeamDAO, TeamLoadEnum
from teampass.user.storage import User


def members_count_formatter(model: TeamModel, _: Column[Any]) -> str:
    """Форматтер для количества участников"""
    return str(len(model.members))


def captain_name_formatter(model: TeamModel, _: Column[Any]) -> str:
    """Форматтер для имени капитана"""
    for member in model.members:
        if member.is_captain:
            return f"{member.student.first_name} {member.student.last_name}"
    return "Не назначен"


class TeamView(ModelView, model=TeamModel):
    name: ClassVar[str] = "Команда"
    name_plural: ClassVar[str] = "Команды"
    category: ClassVar[str] = "Команды"
    icon: ClassVar[str] = "fa-solid fa-users"

    column_labels: ClassVar[dict[MODEL_ATTR, str]] = {
        TeamModel.name: "Название команды",
        TeamModel.created_at: "Создана",
        TeamModel.updated_at: "Обновлена",
        "members_count": "Участников",
        "captain_name": "Капитан",
    }

    column_list: ClassVar[Sequence[MODEL_ATTR]] = [
        TeamModel.name,
        "members_count",
        "captain_name",
    ]

    column_details_list: ClassVar[Sequence[MODEL_ATTR]] = [
        TeamModel.name,
        TeamModel.created_at,
        TeamModel.updated_at,
    ]

    column_formatters: ClassVar[dict[MODEL_ATTR, Any]] = {
        TeamModel.created_at: created_at_formatter,
        TeamModel.updated_at: updated_at_formatter,
        "members_count": members_count_formatter,
        "captain_name": captain_name_formatter,
    }

    column_formatters_detail: ClassVar[dict[MODEL_ATTR, Any]] = {
        TeamModel.created_at: created_at_formatter,
        TeamModel.updated_at: updated_at_formatter,
    }

    column_searchable_list: ClassVar[Sequence[MODEL_ATTR]] = [
        TeamModel.name,
    ]

    form_columns: ClassVar[Sequence[MODEL_ATTR]] = [TeamModel.name]

    can_create: ClassVar[bool] = True
    can_edit: ClassVar[bool] = True
    can_delete: ClassVar[bool] = True

    details_template: ClassVar[str] = "team_details.html"

    @override
    def list_query(self, request: Request) -> Select[Any]:
        stmt = super().list_query(request)
        return stmt.options(selectinload(TeamModel.members).selectinload(User.student))

    @expose("/add-member/{team_id}", methods=["POST"])
    @inject_from_request
    async def add_member(
        self,
        request: Request,
        invite_to_team_method: FromDishka[InviteToTeamMethod] = INJECT,
        accept_invitation_method: FromDishka[AcceptInvitationMethod] = INJECT,
        team_dao: FromDishka[TeamDAO] = INJECT,
    ):
        """Добавление участника в команду"""
        team_id = request.path_params.get("team_id")
        if not team_id:
            return HTMLResponse(content="team_id required", status_code=400)

        form = await request.form()
        invited_user_id = form.get("user_id")

        if not invited_user_id or not isinstance(invited_user_id, str):
            return RedirectResponse(url=f"/team/details/{team_id}", status_code=303)

        try:
            team = await team_dao.find_by_id(
                UUID(team_id), includes=[TeamLoadEnum.MEMBERS]
            )
            if team is None or team.captain is None:
                return RedirectResponse(url=f"/team/details/{team_id}", status_code=303)

            invitation = await invite_to_team_method(
                InviteToTeamCommand(
                    user_id=team.captain.id, invited_user_id=UUID(invited_user_id)
                )
            )
            await accept_invitation_method(
                AcceptInvitationCommand(
                    user_id=UUID(invited_user_id), invitation_id=invitation.id
                )
            )

        except Exception as e:
            print(f"Error adding member: {e}")

        return RedirectResponse(url=f"/team/details/{team_id}", status_code=303)

    @expose("/remove-member/{team_id}", methods=["POST"])
    @inject_from_request
    async def remove_member(
        self,
        request: Request,
        leave_team_method: FromDishka[LeaveTeamMethod] = INJECT,
    ):
        """Удаление участника из команды"""
        team_id = request.path_params.get("team_id")
        if not team_id:
            return HTMLResponse(content="team_id required", status_code=400)

        form = await request.form()
        user_id = form.get("user_id")

        if user_id and isinstance(user_id, str):
            try:
                command = LeaveTeamCommand(user_id=UUID(user_id))
                await leave_team_method(command)
            except Exception as e:
                print(f"Error removing member: {e}")

        return RedirectResponse(url=f"/team/details/{team_id}", status_code=303)

    @expose("/change-captain/{team_id}", methods=["POST"])
    @inject_from_request
    async def change_captain(
        self,
        request: Request,
        transfer_captaincy_method: FromDishka[TransferCaptaincyMethod] = INJECT,
        team_dao: FromDishka[TeamDAO] = INJECT,
    ):
        """Смена капитана команды"""
        team_id = request.path_params.get("team_id")
        if not team_id:
            return HTMLResponse(content="team_id required", status_code=400)

        form = await request.form()
        user_id = form.get("user_id")

        if user_id and isinstance(user_id, str):
            team = await team_dao.find_by_id(
                UUID(team_id), includes=[TeamLoadEnum.MEMBERS]
            )

            if team and team.captain:
                try:
                    command = TransferCaptaincyCommand(
                        user_id=team.captain.id, new_captain_id=UUID(user_id)
                    )
                    await transfer_captaincy_method(command)
                except Exception as e:
                    print(f"Error changing captain: {e}")

        return RedirectResponse(url=f"/team/details/{team_id}", status_code=303)

    @expose("/get-members/{team_id}", methods=["GET"])
    @inject_from_request
    async def get_members(
        self, request: Request, team_dao: FromDishka[TeamDAO] = INJECT
    ):
        """API для получения участников команды"""

        team_id = request.path_params.get("team_id")

        if not team_id:
            return HTMLResponse(content=json.dumps([]), media_type="application/json")

        team = await team_dao.find_by_id(UUID(team_id), includes=[TeamLoadEnum.MEMBERS])
        if not team:
            return HTMLResponse(content=json.dumps([]), media_type="application/json")

        captain = team.captain

        members = []
        for member in team.members:
            student = member.student

            full_name = (
                f"{student.last_name} {student.first_name} "
                + f"{student.patronymic or ''}".strip()
            )
            members.append(
                {
                    "id": str(member.id),
                    "full_name": full_name,
                    "email": member.email,
                    "is_captain": captain == member if captain else False,
                    "user_details_url": f"/admin/user/details/{member.id}",
                }
            )

        return HTMLResponse(
            content=json.dumps(members, default=str), media_type="application/json"
        )

    @expose("/get-available-users/{team_id}", methods=["GET"])
    @inject_from_request
    async def get_available_users(
        self, request: Request, session: FromDishka[AsyncSession] = INJECT
    ):
        """API для получения доступных пользователей (без команды)"""

        team_id = request.path_params.get("team_id")

        if not team_id:
            return HTMLResponse(content=json.dumps([]), media_type="application/json")

        stmt = (
            select(User)
            .where(User.team_id.is_(None))
            .options(selectinload(User.student))
        )
        result = await session.execute(stmt)
        all_users = result.scalars().all()

        available_users = []
        for user in all_users:
            student = user.student if hasattr(user, "student") else None
            first_name = getattr(student, "first_name", "") if student else ""
            last_name = getattr(student, "last_name", "") if student else ""
            patronymic = getattr(student, "patronymic", "") if student else ""

            full_name = f"{last_name} {first_name} {patronymic}".strip()
            if not full_name:
                full_name = user.email or str(user.id)

            available_users.append(
                {"id": str(user.id), "full_name": full_name, "email": user.email}
            )

        return HTMLResponse(
            content=json.dumps(available_users, default=str),
            media_type="application/json",
        )
