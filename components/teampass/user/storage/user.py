from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Index, String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, relationship
from teampass.database import BaseDAO, BaseDAOFactory, BaseModel

from .student_profile import StudentProfile

if TYPE_CHECKING:
    from teampass.team.storage import Team

    from .student import Student


class User(BaseModel):
    __tablename__: str = "user"
    __table_args__: tuple[Any, ...] = (
        Index(
            "uq_team_captain",
            "team_id",
            unique=True,
            postgresql_where="is_captain = true",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    student_id: Mapped[UUID] = mapped_column(
        ForeignKey("student.id", ondelete="CASCADE"), unique=True, index=True
    )
    team_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("team.id", ondelete="SET NULL"), index=True
    )
    is_captain: Mapped[bool] = mapped_column(default=False)

    student: Mapped[Student] = relationship(back_populates="user")
    team: Mapped[Team | None] = relationship(back_populates="members")
    student_profile: Mapped[StudentProfile] = relationship(
        back_populates="user", passive_deletes=True
    )


class UserDAO(BaseDAO[User, UUID]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def create(
        self,
        email: str,
        password_hash: str,
        student_id: UUID,
    ) -> User:
        obj = User(
            email=email,
            password_hash=password_hash,
            student_id=student_id,
            student_profile=StudentProfile(),
        )
        await self.save(obj)
        return obj

    async def find_by_student_id(self, student_id: UUID) -> User | None:
        stmt = select(User).where(User.student_id == student_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()


class UserDAOFactory(BaseDAOFactory[UserDAO]):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_maker, UserDAO)
