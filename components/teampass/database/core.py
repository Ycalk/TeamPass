from abc import ABC, abstractmethod
from collections.abc import (
    AsyncGenerator,
    AsyncIterable,
    Callable,
    Sequence,
)
from contextlib import asynccontextmanager
from datetime import datetime
from enum import StrEnum
from typing import Any, NewType

import structlog
from dishka import Provider, Scope, provide
from dishka.dependency_source import CompositeDependencySource
from opentelemetry import trace
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm.interfaces import ORMOption
from sqlalchemy.types import TIMESTAMP

from .settings import DatabaseSettings

DatabaseUrl = NewType("DatabaseUrl", str)


class BaseModel(AsyncAttrs, DeclarativeBase):
    __abstract__: bool = True
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class BaseDAO[Model: BaseModel, Id, LoadEnum: StrEnum](ABC):
    def __init__(self, session: AsyncSession, model: type[Model]):
        self._session: AsyncSession = session
        self.model: type[Model] = model

    @property
    @abstractmethod
    def _load_mapper(self) -> dict[LoadEnum, ORMOption | Sequence[ORMOption]]:
        pass

    def get_options(self, includes: Sequence[LoadEnum]) -> Sequence[ORMOption]:
        options: list[ORMOption] = []
        for include in includes:
            option = self._load_mapper.get(include)
            if option is None:
                raise ValueError(f"Invalid include option: {include}")
            if isinstance(option, Sequence):
                options.extend(option)
            else:
                options.append(option)
        return options

    async def save(self, obj: Model) -> Model:
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(
            obj,
            attribute_names=[c.key for c in obj.__table__.columns],
        )
        return obj

    async def find_by_id(
        self, id: Id, includes: Sequence[LoadEnum] | None = None
    ) -> Model | None:
        return await self._session.get(
            self.model,
            id,
            options=self.get_options(includes) if includes is not None else None,
            populate_existing=includes is not None,
        )

    async def list(
        self,
        skip: int = 0,
        limit: int | None = None,
        includes: Sequence[LoadEnum] | None = None,
    ) -> Sequence[Model]:
        stmt = select(self.model).offset(skip)
        if includes is not None:
            stmt = stmt.options(*self.get_options(includes))
        if limit is not None:
            stmt = stmt.limit(limit)
        result = (await self._session.execute(stmt)).scalars().all()
        return result

    async def exists_by_id(self, id: Id) -> bool:
        return await self.find_by_id(id) is not None

    async def commit(self) -> None:
        await self._session.commit()


class BaseDAOFactory[DAO: BaseDAO[Any, Any, Any]]:
    def __init__(
        self,
        session_maker: async_sessionmaker[AsyncSession],
        dao_cls: Callable[[AsyncSession], DAO],
    ) -> None:
        self._session_maker: async_sessionmaker[AsyncSession] = session_maker
        self.dao_cls: Callable[[AsyncSession], DAO] = dao_cls

    @asynccontextmanager
    async def __call__(self) -> AsyncGenerator[DAO, None]:
        async with self._session_maker() as session:
            yield self.dao_cls(session)

    def __new__(cls, *args: Any, **kwargs: Any):
        if cls is BaseDAOFactory:
            raise TypeError(f"Only subclasses of {cls.__name__} can be instantiated")
        return super().__new__(cls)


class _DAOFactory:
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    def __call__[T_DAO: BaseDAO[Any, Any, Any]](
        self,
        dao_cls: Callable[[AsyncSession], T_DAO],
    ) -> T_DAO:
        return dao_cls(self._session)

    async def commit(self) -> None:
        await self._session.commit()


class MultipleDAOFactory:
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        self._session_maker: async_sessionmaker[AsyncSession] = session_maker

    @asynccontextmanager
    async def __call__(self) -> AsyncGenerator[_DAOFactory, None]:
        async with self._session_maker() as session:
            yield _DAOFactory(session)


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> DatabaseSettings:
        return DatabaseSettings()  # type: ignore # pyright: ignore

    @provide(scope=Scope.APP)
    def database_url(
        self,
        database_settings: DatabaseSettings,
    ) -> DatabaseUrl:
        url = (
            f"postgresql+asyncpg://{database_settings.postgres_user}"
            + f":{database_settings.postgres_password}"
            + f"@{database_settings.postgres_host}"
            + f":{database_settings.postgres_port}"
            + f"/{database_settings.postgres_db}"
        )
        return DatabaseUrl(url)

    @provide(scope=Scope.APP)
    async def engine(
        self,
        database_url: DatabaseUrl,
        database_settings: DatabaseSettings,
    ) -> AsyncIterable[AsyncEngine]:
        logger = structlog.get_logger("database")
        engine = create_async_engine(
            database_url,
            echo=False,
            pool_size=database_settings.postgres_pool_size,
            max_overflow=database_settings.postgres_max_overflow,
            pool_pre_ping=True,
            connect_args={
                "server_settings": {
                    "timezone": "UTC",
                }
            },
            isolation_level="READ COMMITTED",
        )
        SQLAlchemyInstrumentor().instrument(
            engine=engine.sync_engine,
            tracer_provider=trace.get_tracer_provider(),
            enable_commenter=True,
            commenter_options={"trace_id": True, "span_id": True},
        )
        logger.info("database_engine_created")
        try:
            yield engine
        finally:
            logger.info("disposing_database_engine")
            await engine.dispose()

    @provide(scope=Scope.APP)
    def session_maker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    @provide(scope=Scope.REQUEST)
    async def session(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with session_maker() as session:
            yield session

    multiple_dao_factory: CompositeDependencySource = provide(
        MultipleDAOFactory, scope=Scope.APP
    )
