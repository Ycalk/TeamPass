from __future__ import annotations

from collections.abc import Sequence
from enum import StrEnum
from typing import Any, override
from uuid import UUID

from sqlalchemy import ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, joinedload, mapped_column, relationship
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm.interfaces import ORMOption
from teampass.database import BaseDAO, BaseDAOFactory, BaseModel
from teampass.user.storage import User


class Report(BaseModel):
    __tablename__: str = "report"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), index=True
    )
    content: Mapped[dict[str, Any]] = mapped_column(JSONB)

    owner: Mapped[User] = relationship(back_populates="reports")


class ReportLoadEnum(StrEnum):
    OWNER = "owner"


class ReportDAO(BaseDAO[Report, UUID, ReportLoadEnum]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Report)

    @property
    @override
    def _load_mapper(
        self,
    ) -> dict[ReportLoadEnum, ORMOption | Sequence[ORMOption]]:
        return {ReportLoadEnum.OWNER: joinedload(Report.owner)}

    @override
    async def save(self, obj: Report) -> Report:
        flag_modified(obj, "content")
        return await super().save(obj)

    async def create(self, content: dict[str, Any], owner_id: UUID) -> Report:
        obj = Report(content=content, owner_id=owner_id)
        await self.save(obj)
        return obj


class ReportDAOFactory(BaseDAOFactory[ReportDAO]):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_maker, ReportDAO)
