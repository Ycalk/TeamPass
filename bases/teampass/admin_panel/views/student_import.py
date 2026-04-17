import csv
from io import StringIO
from typing import Annotated, ClassVar

from dishka.integrations.starlette import FromDishka
from sqladmin import BaseView, expose
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from teampass.admin_panel.utils import INJECT, inject_from_request
from teampass.user.storage.student import Student as StudentModel

AsyncSessionDep = Annotated[AsyncSession, FromDishka()]


class StudentImportView(BaseView):
    name: ClassVar[str] = "Импорт студентов CSV"
    identity: ClassVar[str] = "student_import"
    category: ClassVar[str] = "Пользователи"
    icon: ClassVar[str] = "fa-solid fa-file-import"

    @inject_from_request
    @expose("/student-import", methods=["GET", "POST"])
    async def student_import(
        self,
        request: Request,
        session: AsyncSessionDep = INJECT,
    ):
        context = {
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

        if not csv_file.filename.lower().endswith(".csv"):
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
        created = 0
        skipped = 0

        async with session.begin():
            for row in reader:
                try:
                    student_id = row["student_id"].strip()
                    first_name = row["first_name"].strip()
                    last_name = row["last_name"].strip()
                    patronymic = row.get("patronymic", "").strip() or None
                except KeyError:
                    skipped += 1
                    continue
                if not all([student_id, first_name, last_name]):
                    skipped += 1
                    continue

                # Проверяем, есть ли уже студент с таким student_id
                stmt = select(StudentModel).where(StudentModel.student_id == student_id)
                result = await session.execute(stmt)
                if result.scalar_one_or_none():
                    skipped += 1
                    continue

                student = StudentModel(
                    student_id=student_id,
                    first_name=first_name,
                    last_name=last_name,
                    patronymic=patronymic,
                )
                session.add(student)
                created += 1

        context["success"] = created
        context["skipped"] = skipped
        context["message"] = (
            f"✅ {created} студент(ов) добавлено | ⚠️ {skipped} пропущено"
        )

        return await self.templates.TemplateResponse(
            request,
            "student_import.html",
            context,
        )
