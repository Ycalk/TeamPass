import json
from collections.abc import Sequence
from typing import Any, ClassVar
from uuid import UUID

from dishka.integrations.starlette import FromDishka
from sqladmin import ModelView, expose
from sqladmin._types import MODEL_ATTR
from sqlalchemy import Column, select
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
from teampass.user.storage import User


def members_count_formatter(model: TeamModel, _: Column) -> str:
    """Форматтер для количества участников"""
    try:
        if hasattr(model, "members") and model.members is not None:
            return str(len(model.members))
        return "0"
    except:
        return "0"


def captain_name_formatter(model: TeamModel, _: Column) -> str:
    """Форматтер для имени капитана"""
    try:
        if hasattr(model, "members") and model.members:
            for member in model.members:
                if getattr(member, "is_captain", False):
                    if hasattr(member, "student") and member.student:
                        student = member.student
                        first_name = getattr(student, "first_name", "")
                        last_name = getattr(student, "last_name", "")
                        if first_name or last_name:
                            return f"{last_name} {first_name}".strip()
                    return member.email or "Капитан"
        return "Не назначен"
    except Exception:
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

    form_columns = ["name"]

    can_create: ClassVar[bool] = True
    can_edit: ClassVar[bool] = True
    can_delete: ClassVar[bool] = True

    details_template = "team_details.html"

    async def get_list(self, request: Request) -> list[TeamModel]:
        """Переопределяем метод для предварительной загрузки участников"""
        async with self.session_maker() as session:
            stmt = select(TeamModel).options(
                selectinload(TeamModel.members).selectinload(User.student)
            )
            result = await session.execute(stmt)
            return result.scalars().all()

    async def get_object_by_id(self, id: str) -> TeamModel | None:
        """Загружаем команду с участниками"""
        async with self.session_maker() as session:
            stmt = (
                select(TeamModel)
                .where(TeamModel.id == id)
                .options(selectinload(TeamModel.members).selectinload(User.student))
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    @expose("/add-member/{team_id}", methods=["POST"])
    @inject_from_request
    async def add_member(
        self,
        request: Request,
        invite_to_team_method: FromDishka[InviteToTeamMethod] = INJECT,
        accept_invitation_method: FromDishka[AcceptInvitationMethod] = INJECT,
    ):
        """Добавление участника в команду"""
        team_id = request.path_params.get("team_id")
        if not team_id:
            return HTMLResponse(content="team_id required", status_code=400)

        form = await request.form()
        invited_user_id = form.get("user_id")

        if not invited_user_id:
            return RedirectResponse(url=f"/team/details/{team_id}", status_code=303)

        try:
            async with self.session_maker() as session:
                stmt = (
                    select(TeamModel)
                    .where(TeamModel.id == team_id)
                    .options(selectinload(TeamModel.members))
                )
                result = await session.execute(stmt)
                team = result.scalar_one_or_none()

                if not team or not team.captain:
                    print(f"Team {team_id} has no captain")
                    return RedirectResponse(
                        url=f"/team/details/{team_id}", status_code=303
                    )

            invite_command = InviteToTeamCommand(
                user_id=team.captain.id, invited_user_id=UUID(invited_user_id)
            )
            invitation = await invite_to_team_method(invite_command)

            accept_command = AcceptInvitationCommand(
                user_id=UUID(invited_user_id), invitation_id=invitation.id
            )
            await accept_invitation_method(accept_command)

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

        if user_id:
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
    ):
        """Смена капитана команды"""
        team_id = request.path_params.get("team_id")
        if not team_id:
            return HTMLResponse(content="team_id required", status_code=400)

        form = await request.form()
        user_id = form.get("user_id")

        if user_id:
            async with self.session_maker() as session:
                stmt = (
                    select(TeamModel)
                    .where(TeamModel.id == team_id)
                    .options(selectinload(TeamModel.members))
                )
                result = await session.execute(stmt)
                team = result.scalar_one_or_none()

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
    async def get_members(self, request: Request, **kwargs):
        """API для получения участников команды"""

        team_id = request.path_params.get("team_id")

        if not team_id:
            return HTMLResponse(content=json.dumps([]), media_type="application/json")

        async with self.session_maker() as session:
            stmt = (
                select(TeamModel)
                .where(TeamModel.id == team_id)
                .options(selectinload(TeamModel.members).selectinload(User.student))
            )
            result = await session.execute(stmt)
            team = result.scalar_one_or_none()

        if not team:
            return HTMLResponse(content=json.dumps([]), media_type="application/json")

        captain = team.captain

        members = []
        for member in team.members:
            student = member.student if hasattr(member, "student") else None
            first_name = getattr(student, "first_name", "") if student else ""
            last_name = getattr(student, "last_name", "") if student else ""
            patronymic = getattr(student, "patronymic", "") if student else ""

            full_name = f"{last_name} {first_name} {patronymic}".strip()
            if not full_name:
                full_name = member.email or str(member.id)

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
    async def get_available_users(self, request: Request, **kwargs):
        """API для получения доступных пользователей (без команды)"""

        team_id = request.path_params.get("team_id")

        if not team_id:
            return HTMLResponse(content=json.dumps([]), media_type="application/json")

        async with self.session_maker() as session:
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
