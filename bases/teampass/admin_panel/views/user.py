from collections.abc import Sequence
from typing import ClassVar

from pydantic import ValidationError
from sqladmin import ModelView
from sqladmin._types import MODEL_ATTR
from starlette.requests import Request
from teampass.admin_panel.utils import AdminSession, AdminType
from teampass.user.storage.user import User as UserModel


class UserView(ModelView, model=UserModel):
    name: ClassVar[str] = "Пользователь"
    name_plural: ClassVar[str] = "Пользователи"
    category: ClassVar[str] = "Пользователи"
    icon: ClassVar[str] = "fa-solid fa-users"

    column_list: ClassVar[Sequence[MODEL_ATTR]] = [
        UserModel.id,
        UserModel.email,
        UserModel.student_id,
        UserModel.is_captain,
    ]

    column_searchable_list: ClassVar[Sequence[MODEL_ATTR]] = [
        UserModel.email,
        UserModel.student_id,
    ]

    form_excluded_columns = (
        UserModel.created_at,
        UserModel.updated_at,
    )

    column_formatters = {
        UserModel.student: lambda m, a, b: (
            m.student.student_id if m.student else "Нет студента"
        )
    }

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
