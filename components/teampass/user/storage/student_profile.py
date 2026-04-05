from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, relationship
from teampass.database import BaseDAO, BaseDAOFactory, BaseModel

if TYPE_CHECKING:
    from .user import User


class StudentProfile(BaseModel):
    __tablename__: str = "student_profile"
    __table_args__: tuple[Any, ...] = (
        CheckConstraint(
            "phone_number ~ '^\\+[1-9]\\d{1,14}$'", name="chk_phone_format"
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), unique=True, index=True
    )
    telegram_username: Mapped[str | None] = mapped_column(String(255))
    vk_profile_link: Mapped[str | None] = mapped_column(String(255))
    phone_number: Mapped[str | None] = mapped_column(String(255))
    strengths_text: Mapped[str | None] = mapped_column(Text)
    weaknesses_text: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="student_profile")


class StudentProfileDAO(BaseDAO[StudentProfile, UUID]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, StudentProfile)

    async def create(
        self,
        user_id: UUID,
        *,
        telegram_username: str | None = None,
        vk_profile_link: str | None = None,
        phone_number: str | None = None,
        strengths_text: str | None = None,
        weaknesses_text: str | None = None,
    ) -> StudentProfile:
        obj = StudentProfile(
            user_id=user_id,
            telegram_username=telegram_username,
            vk_profile_link=vk_profile_link,
            phone_number=phone_number,
            strengths_text=strengths_text,
            weaknesses_text=weaknesses_text,
        )
        await self.save(obj)
        return obj


class StudentProfileDAOFactory(BaseDAOFactory[StudentProfileDAO]):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_maker, StudentProfileDAO)
