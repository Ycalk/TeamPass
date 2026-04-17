from collections.abc import Callable, Sequence
from typing import Any, ClassVar

from sqladmin import ModelView
from sqladmin._types import MODEL_ATTR
from sqlalchemy import Column
from teampass.admin_panel.formatters import created_at_formatter, updated_at_formatter
from teampass.user.storage.user import User as UserModel


def student_formatter(model: type, _: Column[Any]) -> str:
    if not isinstance(model, UserModel):
        raise TypeError("Model must be an instance of UserModel")
    return (
        f"{model.student.last_name} {model.student.first_name} "
        f"{model.student.patronymic}"
    )


def team_formatter(model: type, _: Column[Any]) -> str:
    if not isinstance(model, UserModel):
        raise TypeError("Model must be an instance of UserModel")
    return model.team.name if model.team else ""


class UserView(ModelView, model=UserModel):
    name: ClassVar[str] = "Пользователь"
    name_plural: ClassVar[str] = "Пользователи"
    category: ClassVar[str] = "Пользователи"
    icon: ClassVar[str] = "fa-solid fa-users"

    column_labels: ClassVar[dict[MODEL_ATTR, str]] = {
        UserModel.email: "Email",
        UserModel.student: "Студент",
        UserModel.student_profile: "Профиль",
        UserModel.team: "Команда",
        UserModel.created_at: "Дата создания (UTC)",
        UserModel.updated_at: "Дата обновления (UTC)",
    }

    column_list: ClassVar[Sequence[MODEL_ATTR]] = [
        UserModel.email,
        UserModel.student,
        UserModel.student_profile,
        UserModel.team,
    ]
    column_formatters: ClassVar[
        dict[MODEL_ATTR, Callable[[type, Column[Any]], str]]
    ] = {
        UserModel.student: student_formatter,
        UserModel.student_profile: lambda model, _: "Профиль",
        UserModel.team: team_formatter,
    }

    column_details_list: ClassVar[Sequence[MODEL_ATTR]] = [
        UserModel.email,
        UserModel.student,
        UserModel.student_profile,
        UserModel.team,
        UserModel.created_at,
        UserModel.updated_at,
    ]
    column_formatters_detail: ClassVar[
        dict[MODEL_ATTR, Callable[[type, Column[Any]], str]]
    ] = {
        UserModel.student: student_formatter,
        UserModel.student_profile: lambda model, _: "Профиль",
        UserModel.team: team_formatter,
        UserModel.created_at: created_at_formatter,
        UserModel.updated_at: updated_at_formatter,
    }

    column_searchable_list: ClassVar[Sequence[MODEL_ATTR]] = [
        UserModel.email,
    ]

    form_excluded_columns: ClassVar[Sequence[MODEL_ATTR]] = (
        UserModel.created_at,
        UserModel.updated_at,
    )

    can_create: ClassVar[bool] = False
    can_edit: ClassVar[bool] = True
    can_delete: ClassVar[bool] = True
