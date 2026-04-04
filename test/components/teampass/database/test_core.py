import pytest
from sqlalchemy.orm import Mapped, mapped_column
from teampass.database.core import (
    BaseDAOFactory,
    BaseModel,
    DatabaseProvider,
)
from teampass.database.settings import DatabaseSettings


def test_base_model_columns():
    class DummyModel(BaseModel):
        __tablename__: str = "dummy"
        id: Mapped[int] = mapped_column(primary_key=True)

    assert "created_at" in DummyModel.__table__.columns
    assert "updated_at" in DummyModel.__table__.columns
    assert "id" in DummyModel.__table__.columns


def test_base_dao_factory_cannot_be_instantiated():
    with pytest.raises(
        TypeError, match="Only subclasses of BaseDAOFactory can be instantiated"
    ):
        BaseDAOFactory(None, None)  # type: ignore # pyright: ignore


def test_base_dao_factory_subclass_can_be_instantiated():
    class MyDAOFactory(BaseDAOFactory):  # pyright: ignore
        def __init__(self):  # pyright: ignore
            pass

    factory = MyDAOFactory()
    assert factory is not None


def test_database_provider_url_generation():
    provider = DatabaseProvider()
    settings = DatabaseSettings(
        postgres_user="test_usr",
        postgres_password="test_password",
        postgres_host="localhost",
        postgres_port=5432,
        postgres_db="test_db",
    )

    url = provider.database_url(settings)
    assert url == "postgresql+asyncpg://test_usr:test_password@localhost:5432/test_db"
