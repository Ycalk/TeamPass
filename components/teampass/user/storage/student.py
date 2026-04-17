from __future__ import annotations

from collections.abc import Sequence
from enum import StrEnum
from typing import TYPE_CHECKING, override
from uuid import UUID

from sqlalchemy import String, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, joinedload, mapped_column, relationship
from sqlalchemy.orm.interfaces import ORMOption
from teampass.database import BaseDAO, BaseDAOFactory, BaseModel

if TYPE_CHECKING:
    from .user import User


class Student(BaseModel):
    __tablename__: str = "student"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    student_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255))
    patronymic: Mapped[str | None] = mapped_column(String(255))

    user: Mapped[User | None] = relationship(
        back_populates="student", passive_deletes=True
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


class StudentDAOFactory(BaseDAOFactory[StudentDAO]):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_maker, StudentDAO)
