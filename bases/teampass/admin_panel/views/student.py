from collections.abc import Sequence
from typing import ClassVar

from pydantic import ValidationError
from sqladmin import ModelView
from sqladmin._types import MODEL_ATTR
from starlette.requests import Request
from teampass.admin_panel.utils import AdminSession, AdminType
from teampass.user.storage.student import Student as StudentModel


class StudentView(ModelView, model=StudentModel):
    name: ClassVar[str] = "Студент"
    name_plural: ClassVar[str] = "Студенты"
    category: ClassVar[str] = "Пользователи"
    icon: ClassVar[str] = "fa-solid fa-user-graduate"

    column_list: ClassVar[Sequence[MODEL_ATTR]] = [
        StudentModel.student_id,
        StudentModel.first_name,
        StudentModel.last_name,
        StudentModel.patronymic,
    ]

    column_searchable_list: ClassVar[Sequence[MODEL_ATTR]] = [
        StudentModel.student_id,
        StudentModel.first_name,
        StudentModel.last_name,
    ]

    form_excluded_columns = (
        StudentModel.created_at,
        StudentModel.updated_at,
        StudentModel.user,
    )

    can_create: ClassVar[bool] = True
    can_edit: ClassVar[bool] = True
    can_delete: ClassVar[bool] = True

    def is_accessible(self, request: Request) -> bool:
        try:
            admin_session = AdminSession.model_validate(request.session)
            return admin_session.admin_type in (AdminType.SUPER_ADMIN, AdminType.ADMIN)
        except ValidationError:
            return False

    def is_visible(self, request: Request) -> bool:
        try:
            admin_session = AdminSession.model_validate(request.session)
            return admin_session.admin_type in (AdminType.SUPER_ADMIN, AdminType.ADMIN)
        except ValidationError:
            return False
