from typing import Any, ClassVar, override

from dishka.integrations.starlette import FromDishka
from pydantic import SecretStr
from sqladmin import BaseView, expose
from starlette.requests import Request
from teampass.admin import ChangeAdminPasswordCommand, ChangeAdminPasswordMethod
from teampass.admin_panel.authentication import AdminSession, AdminType
from teampass.admin_panel.inject import INJECT, inject_from_request
from teampass.domain_core import DomainException


class ChangePasswordView(BaseView):
    name: ClassVar[str] = "Смена пароля"
    icon: ClassVar[str] = "fa-solid fa-key"
    category: ClassVar[str] = "Настройки"

    @expose("/change-password", methods=["GET", "POST"])
    @inject_from_request
    async def change_password_page(
        self,
        request: Request,
        change_admin_password_method: FromDishka[ChangeAdminPasswordMethod] = INJECT,
    ):
        context: dict[str, Any] = {"request": request, "error": None, "success": None}

        if request.method == "POST":
            form = await request.form()
            old_password = form.get("old_password")
            new_password = form.get("new_password")
            confirm_password = form.get("confirm_password")

            if new_password != confirm_password:
                context["error"] = "Новые пароли не совпадают"
                return await self.templates.TemplateResponse(
                    request, "change_password.html", context
                )

            if not isinstance(old_password, str) or not isinstance(new_password, str):
                context["error"] = "Неверный формат пароля"
                return await self.templates.TemplateResponse(
                    request, "change_password.html", context
                )

            admin_session = AdminSession.model_validate(request.session)

            if admin_session.id is None:
                context["error"] = (
                    "Супер-админ не может изменить пароль через эту форму"
                )
                return await self.templates.TemplateResponse(
                    request, "change_password.html", context
                )

            try:
                await change_admin_password_method(
                    ChangeAdminPasswordCommand(
                        admin_id=admin_session.id,
                        current_password=SecretStr(old_password),
                        new_password=SecretStr(new_password),
                    )
                )
                context["success"] = "Пароль успешно изменен"
            except DomainException as e:
                context["error"] = str(e)

        return await self.templates.TemplateResponse(
            request, "change_password.html", context
        )

    @override
    def is_accessible(self, request: Request) -> bool:
        admin_session = AdminSession.model_validate(request.session)
        return admin_session.admin_type == AdminType.ADMIN

    @override
    def is_visible(self, request: Request) -> bool:
        admin_session = AdminSession.model_validate(request.session)
        return admin_session.admin_type == AdminType.ADMIN
