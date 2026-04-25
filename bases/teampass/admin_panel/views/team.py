from collections.abc import Sequence, Callable
from typing import Any, ClassVar

from sqladmin import ModelView
from sqladmin._types import MODEL_ATTR
from sqlalchemy import Column
from teampass.team.storage import Team as TeamModel
from teampass.team.dto import Team as TeamDTO
from teampass.team.storage import TeamDAO
from teampass.user.storage import UserDAO
from teampass.admin_panel.formatters import (
    created_at_formatter,
    updated_at_formatter,
)


def team_name_formatter(
    model: type, _: Column[Any]
) -> str:
    if not isinstance(model, TeamModel):
        raise TypeError("Model must be an instance of TeamModel")
    return str(model.name)


def members_count_formatter(
    model: type, _: Column[Any]
) -> str:
    if not isinstance(model, TeamModel):
        raise TypeError("Model must be an instance of TeamModel")
    return str(len(model.members))


class TeamView(ModelView, model=TeamModel):
    name: ClassVar[str] = "Команда"
    name_plural: ClassVar[str] = "Команды"
    category: ClassVar[str] = "Команды"
    icon: ClassVar[str] = "fa-solid fa-users"

    column_labels: ClassVar[dict[MODEL_ATTR, str]] = {
        TeamModel.name: "Название команды",
        TeamModel.created_at: created_at_formatter,
        TeamModel.updated_at: updated_at_formatter,
    }

    column_list: ClassVar[Sequence[MODEL_ATTR]] = [
        TeamModel.name,
    ]

    column_details_list: ClassVar[Sequence[MODEL_ATTR]] = [
        TeamModel.name,
        TeamModel.created_at,
        TeamModel.updated_at,
    ]

   

    column_formatters_detail: ClassVar[
        dict[MODEL_ATTR, Callable[[type, Column[Any]], str]]
    ] = {
        TeamModel.created_at: created_at_formatter,
        TeamModel.updated_at: updated_at_formatter,
    }

    column_searchable_list: ClassVar[Sequence[MODEL_ATTR]] = [
        TeamModel.name,
    ]


    form_columns = {
        "name": None,
    }

    can_create: ClassVar[bool] = True
    can_edit: ClassVar[bool] = True 
    can_delete: ClassVar[bool] = True