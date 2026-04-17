import csv
from io import StringIO
from typing import Any, ClassVar

from dishka.integrations.starlette import FromDishka
from sqladmin import BaseView, expose
from starlette.datastructures import UploadFile
from starlette.requests import Request
from teampass.admin_panel.inject import INJECT, inject_from_request
from teampass.user.storage import StudentDAO


class StudentImportView(BaseView):
    name: ClassVar[str] = "Импорт студентов CSV"
    category: ClassVar[str] = "Пользователи"
    icon: ClassVar[str] = "fa-solid fa-file-import"

    @expose("/student-import", methods=["GET", "POST"])
    @inject_from_request
    async def student_import(
        self,
        request: Request,
        student_dao: FromDishka[StudentDAO] = INJECT,
    ):
        context: dict[str, Any] = {
            "request": request,
            "success": 0,
            "skipped": 0,
            "message": None,
        }

        if request.method == "GET":
            return await self.templates.TemplateResponse(
                request,
                "student_import.html",
                context,
            )

        form = await request.form()
        if "csv_file" not in form:
            context["message"] = "❌ Файл не загружен"
            return await self.templates.TemplateResponse(
                request,
                "student_import.html",
                context,
            )

        csv_file = form["csv_file"]

        if (
            not isinstance(csv_file, UploadFile)
            or csv_file.filename is None
            or not csv_file.filename.lower().endswith(".csv")
        ):
            context["message"] = "❌ Разрешены только CSV файлы"
            return await self.templates.TemplateResponse(
                request,
                "student_import.html",
                context,
            )

        content = await csv_file.read()
        try:
            content_str = content.decode("utf-8")
        except UnicodeDecodeError:
            context["message"] = "❌ Ошибка декодирования файла (не UTF‑8)"
            return await self.templates.TemplateResponse(
                request,
                "student_import.html",
                context,
            )

        reader = csv.DictReader(StringIO(content_str))

        for row in reader:
            try:
                student_id = row["student_id"].strip()
                first_name = row["first_name"].strip()
                last_name = row["last_name"].strip()
                patronymic = row.get("patronymic", "").strip() or None
            except KeyError:
                context["skipped"] += 1
                continue
            if not all([student_id, first_name, last_name]):
                context["skipped"] += 1
                continue

            student = await student_dao.find_by_student_id(student_id)
            if student is not None:
                context["skipped"] += 1
                continue

            await student_dao.create(
                student_id=student_id,
                first_name=first_name,
                last_name=last_name,
                patronymic=patronymic,
            )
            context["success"] += 1
            await student_dao.commit()

        context["message"] = (
            f"✅ {context['success']} студент(ов) добавлено | "
            + f"⚠️ {context['skipped']} пропущено"
        )

        return await self.templates.TemplateResponse(
            request,
            "student_import.html",
            context,
        )
