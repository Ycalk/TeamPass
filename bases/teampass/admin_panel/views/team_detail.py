from typing import ClassVar, Annotated

from dishka.integrations.starlette import FromDishka
from sqlalchemy.ext.asyncio import AsyncSession
from sqladmin import BaseView, expose
from sqlalchemy import select
from starlette.requests import Request
from starlette.responses import Response
from starlette.datastructures import FormData


from teampass.team.dto import Team as TeamDTO
from teampass.team.storage import TeamDAO, Team as TeamModel
from teampass.user.storage import UserDAO
from teampass.team.methods import (
    RemoveTeamMemberMethod,
    TransferCaptaincyMethod,
    RenameTeamMethod,
    LeaveTeamMethod,
)
from teampass.admin_panel.inject import INJECT, inject_from_request
from teampass.admin_panel.authentication import AdminSession, AdminType


class TeamDetailView(BaseView):
    name: ClassVar[str] = "Детали команды"
    identity: ClassVar[str] = "team_detail"
    category: ClassVar[str] = "Команды"
    icon: ClassVar[str] = "fa-solid fa-users-viewfinder"


    @expose("/team/{team_id:int}/detail", methods=["GET"])
    async def team_detail(
        self,
        request: Request,
        team_id: int,
    ) -> Response:
        # временно просто возвращаем OK, чтобы проверить маршрут
        return Response(
            content=f"Team ID: {team_id}",
            media_type="text/plain",
        )
        