from __future__ import annotations

from collections.abc import Sequence
from enum import StrEnum
from typing import TYPE_CHECKING, Any, override
from uuid import UUID

from sqlalchemy import Index, String, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, joinedload, mapped_column, relationship
from sqlalchemy.orm.interfaces import ORMOption
from sqlalchemy.sql import ColumnElement
from teampass.database import BaseDAO, BaseDAOFactory, BaseModel

if TYPE_CHECKING:
    from .user import User


class Student(BaseModel):
    __tablename__: str = "student"
    __table_args__: tuple[Any, ...] = (
        Index(
            "ix_student_search_vector_trgm",
            func.concat_ws(
                " ",
                "student_id",
                "first_name",
                "last_name",
                func.coalesce("patronymic", ""),
            ),
            postgresql_using="gin",
            postgresql_ops={
                "concat_ws": "gin_trgm_ops",
            },
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    student_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255))
    patronymic: Mapped[str | None] = mapped_column(String(255))

    user: Mapped[User | None] = relationship(
        back_populates="student", cascade="all, delete-orphan", passive_deletes=True
    )


class StudentLoadEnum(StrEnum):
    USER = "user"


class StudentDAO(BaseDAO[Student, UUID, StudentLoadEnum]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Student)

    @property
    @override
    def _load_mapper(self) -> dict[StudentLoadEnum, ORMOption | Sequence[ORMOption]]:
        return {
            StudentLoadEnum.USER: joinedload(Student.user),
        }

    async def create(
        self,
        student_id: str,
        first_name: str,
        last_name: str,
        patronymic: str | None,
    ) -> Student:
        obj = Student(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
        )
        await self.save(obj)
        return obj

    async def find_by_student_id(
        self, student_id: str, includes: Sequence[StudentLoadEnum] | None = None
    ) -> Student | None:
        stmt = select(Student).where(Student.student_id == student_id)
        if includes is not None:
            stmt = stmt.options(*self.get_options(includes))
            stmt = stmt.execution_options(populate_existing=True)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def search_students(
        self,
        query: str,
        limit: int = 20,
        includes: Sequence[StudentLoadEnum] | None = None,
    ) -> Sequence[Student]:
        if not query or not query.strip():
            return []

        search_vector = func.concat_ws(
            " ",
            Student.student_id,
            Student.first_name,
            Student.last_name,
            func.coalesce(Student.patronymic, ""),
        )

        words = query.strip().split()
        conditions: list[ColumnElement[bool]] = []

        for word in words:
            conditions.append(search_vector.ilike(f"%{word}%"))
        conditions.append(Student.user.has())
        stmt = select(Student).where(and_(*conditions)).limit(limit)

        if includes is not None:
            stmt = stmt.options(*self.get_options(includes))
            stmt = stmt.execution_options(populate_existing=True)

        result = await self._session.execute(stmt)
        return result.scalars().all()


class StudentDAOFactory(BaseDAOFactory[StudentDAO]):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_maker, StudentDAO)
