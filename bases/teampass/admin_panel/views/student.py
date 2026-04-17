from collections.abc import Callable, Sequence
from typing import Any, ClassVar

from sqladmin import ModelView
from sqladmin._types import MODEL_ATTR
from sqlalchemy import Column
from teampass.admin_panel.formatters import created_at_formatter, updated_at_formatter
from teampass.user.storage.student import Student as StudentModel


def user_formatter(model: type, _: Column[Any]) -> str:
    if not isinstance(model, StudentModel):
        raise TypeError("Model must be an instance of StudentModel")
    return "Пользователь" if model.user else ""


class StudentView(ModelView, model=StudentModel):
    name: ClassVar[str] = "Студент"
    name_plural: ClassVar[str] = "Студенты"
    category: ClassVar[str] = "Пользователи"
    icon: ClassVar[str] = "fa-solid fa-user-graduate"

    column_labels: ClassVar[dict[MODEL_ATTR, str]] = {
        StudentModel.student_id: "№ студенческого билета",
        StudentModel.first_name: "Имя",
        StudentModel.last_name: "Фамилия",
        StudentModel.patronymic: "Отчество",
        StudentModel.created_at: "Дата создания (UTC)",
        StudentModel.updated_at: "Дата обновления (UTC)",
        StudentModel.user: "Пользователь",
    }

    column_list: ClassVar[Sequence[MODEL_ATTR]] = [
        StudentModel.student_id,
        StudentModel.last_name,
        StudentModel.first_name,
        StudentModel.patronymic,
    ]
    column_details_list: ClassVar[Sequence[MODEL_ATTR]] = [
        StudentModel.student_id,
        StudentModel.last_name,
        StudentModel.first_name,
        StudentModel.patronymic,
        StudentModel.created_at,
        StudentModel.updated_at,
        StudentModel.user,
    ]
    column_formatters_detail: ClassVar[
        dict[MODEL_ATTR, Callable[[type, Column[Any]], str]]
    ] = {
        StudentModel.created_at: created_at_formatter,
        StudentModel.updated_at: updated_at_formatter,
        StudentModel.user: user_formatter,
    }

    column_searchable_list: ClassVar[Sequence[MODEL_ATTR]] = [
        StudentModel.student_id,
        StudentModel.first_name,
        StudentModel.last_name,
    ]

    form_excluded_columns: ClassVar[Sequence[MODEL_ATTR]] = (
        StudentModel.created_at,
        StudentModel.updated_at,
        StudentModel.user,
    )

    can_create: ClassVar[bool] = True
    can_edit: ClassVar[bool] = True
    can_delete: ClassVar[bool] = True
