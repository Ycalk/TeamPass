from __future__ import annotations

from uuid import UUID

from sqlalchemy import String, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column
from teampass.database import BaseDAO, BaseDAOFactory, BaseModel


class Admin(BaseModel):
    __tablename__: str = "admin"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))


class AdminDAO(BaseDAO[Admin, UUID]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Admin)

    async def create(
        self,
        username: str,
        password_hash: str,
    ) -> Admin:
        obj = Admin(username=username, password_hash=password_hash)
        await self.save(obj)
        return obj

    async def find_by_username(self, username: str) -> Admin | None:
        stmt = select(Admin).where(Admin.username == username)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()


class AdminDAOFactory(BaseDAOFactory[AdminDAO]):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_maker, AdminDAO)
