from __future__ import annotations

from typing import Any, ClassVar, Self, overload

from sqlalchemy import String, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.attributes import flag_modified
from teampass.database import BaseModel

SupportedValueType = str | int | bool | float


class _LiveOptionStorage(BaseModel):
    __tablename__: str = "live_option"
    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    value: Mapped[dict[str, SupportedValueType]] = mapped_column(JSONB)


class OptionDef[T: SupportedValueType]:
    def __init__(self, *, description: str, default_value: T):
        self.description: str = description
        self.default_value: T = default_value
        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    @overload
    def __get__(self, instance: None, owner: type) -> Self: ...

    @overload
    def __get__(self, instance: LiveOptionBase, owner: type) -> T: ...

    def __get__(self, instance: LiveOptionBase | None, owner: type) -> T | Self:
        if instance is None:
            return self
        return instance.values[self.name]  # type: ignore  # pyright: ignore[reportReturnType]

    def __set__(self, instance: LiveOptionBase, value: T) -> None:
        instance.values[self.name] = value


class LiveOptionBase:
    name: ClassVar[str]
    __options__: ClassVar[tuple[OptionDef[Any], ...]]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if "name" not in cls.__dict__:
            raise TypeError(f"Class '{cls.__name__}' must define a 'name' ClassVar.")

        options = []
        for attr_name in dir(cls):
            attr_value = getattr(cls, attr_name)
            if isinstance(attr_value, OptionDef):
                options.append(attr_value)
        cls.__options__ = tuple(options)

    def __init__(self, session: AsyncSession) -> None:
        self.values: dict[str, SupportedValueType] = {
            opt.name: opt.default_value for opt in self.__options__
        }
        self._session: AsyncSession = session

    async def sync(self) -> Self:
        storage = await self._get_storage()
        if storage is None:
            return self
        for opt in self.__options__:
            if opt.name in storage.value:
                value = storage.value[opt.name]
                expected_type = type(opt.default_value)
                if not isinstance(value, expected_type):
                    raise TypeError(
                        f"Invalid type for {opt.name}. "
                        + f"Expected {expected_type.__name__}, "
                        + f"got {type(value).__name__}"
                    )
                self.values[opt.name] = value
        return self

    async def save(self) -> Self:
        storage = await self._get_storage()
        if storage is None:
            storage = _LiveOptionStorage(key=self.name, value=self.values)
            self._session.add(storage)
        else:
            storage.value = self.values
            flag_modified(storage, "value")
        await self._session.flush()
        return self

    async def commit(self) -> None:
        await self._session.commit()

    async def _get_storage(self) -> _LiveOptionStorage | None:
        stmt = select(_LiveOptionStorage).where(_LiveOptionStorage.key == self.name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
