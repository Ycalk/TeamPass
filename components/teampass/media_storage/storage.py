from __future__ import annotations

from collections.abc import Sequence
from enum import StrEnum
from typing import Any, override
from uuid import UUID

from sqlalchemy import ForeignKey, String, event, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.interfaces import ORMOption
from teampass.database import BaseDAO, BaseDAOFactory, BaseModel
from teampass.user.storage import User


class Media(BaseModel):
    __tablename__: str = "media"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), index=True
    )
    mime_type: Mapped[str] = mapped_column(String(255))
    size_bytes: Mapped[int] = mapped_column()
    file_name: Mapped[str] = mapped_column(String(255))

    owner: Mapped[User] = relationship(back_populates="media")


class MediaLoadEnum(StrEnum):
    pass


class MediaDAO(BaseDAO[Media, UUID, MediaLoadEnum]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Media)

    @property
    @override
    def _load_mapper(
        self,
    ) -> dict[MediaLoadEnum, ORMOption | Sequence[ORMOption]]:
        return {}

    async def create(
        self,
        mime_type: str,
        size_bytes: int,
        file_name: str,
        owner_id: UUID,
        id: UUID | None = None,
    ) -> Media:
        obj_data: dict[str, Any] = {
            "mime_type": mime_type,
            "size_bytes": size_bytes,
            "file_name": file_name,
            "owner_id": owner_id,
        }
        if id is not None:
            obj_data["id"] = id
        obj = Media(**obj_data)
        await self.save(obj)
        return obj


class MediaDAOFactory(BaseDAOFactory[MediaDAO]):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_maker, MediaDAO)


@event.listens_for(Media, "before_update")
def receive_before_update(_mapper: Any, _connection: Any, _target: Any) -> None:
    raise RuntimeError("Media records are immutable and cannot be updated.")
