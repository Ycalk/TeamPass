from collections.abc import Sequence
from typing import Any, ClassVar, Final, override

import structlog
from dishka.integrations.starlette import FromDishka
from opentelemetry import trace
from pydantic import SecretStr
from sqladmin import ModelView
from sqladmin._types import MODEL_ATTR
from starlette.requests import Request
from teampass.admin import CreateAdminCommand, CreateAdminMethod
from teampass.admin.storage import Admin as AdminModel
from teampass.admin_panel.utils import (
    INJECT,
    AdminSession,
    AdminType,
    inject_from_request,
)
from wtforms import Form, PasswordField, StringField, validators

_logger: Final[structlog.BoundLogger] = structlog.get_logger()
_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)


class AdminCreateForm(Form):
    username: ClassVar[StringField] = StringField("Логин", [validators.DataRequired()])
    password: ClassVar[StringField] = PasswordField(
        "Пароль", [validators.DataRequired()]
    )


class AdminView(ModelView, model=AdminModel):
    name: ClassVar[str] = "Организатор"
    name_plural: ClassVar[str] = "Организаторы"
    category: ClassVar[str] = "Настройки"
    icon: ClassVar[str] = "fa-solid fa-address-book"
    column_list: ClassVar[Sequence[MODEL_ATTR]] = [
        AdminModel.username,
        AdminModel.created_at,
    ]
    column_details_list: ClassVar[Sequence[MODEL_ATTR]] = [
        AdminModel.id,
        AdminModel.username,
        AdminModel.updated_at,
        AdminModel.created_at,
    ]
    can_create: ClassVar[bool] = True
    can_edit: ClassVar[bool] = False
    can_delete: ClassVar[bool] = False

    @override
    async def scaffold_form(self, rules: list[str] | None = None) -> type[Form]:
        return AdminCreateForm

    @override
    @inject_from_request
    async def insert_model(
        self,
        request: Request,
        data: dict[str, Any],
        create_admin_method: FromDishka[CreateAdminMethod] = INJECT,
    ) -> Any:
        with _tracer.start_as_current_span("admin.create_admin") as span:
            username = data.get("username")
            if not isinstance(username, str):
                raise ValueError("Username must be a string")

            password = data.get("password")
            if not isinstance(password, str):
                raise ValueError("Password must be a string")

            span.set_attribute("username", username)

            new_admin = await create_admin_method(
                CreateAdminCommand(
                    username=username, plain_password=SecretStr(password)
                )
            )
            return AdminModel(id=new_admin.id)

    @override
    def is_accessible(self, request: Request) -> bool:
        admin_session = AdminSession.model_validate(request.session)
        return admin_session.admin_type == AdminType.SUPER_ADMIN

    @override
    def is_visible(self, request: Request) -> bool:
        admin_session = AdminSession.model_validate(request.session)
        return admin_session.admin_type == AdminType.SUPER_ADMIN
