from typing import Any

from sqlalchemy import Column
from teampass.database import BaseModel


def created_at_formatter(model: type, _: Column[Any]) -> str:
    if not isinstance(model, BaseModel):
        raise TypeError("Model must be an instance of BaseModel")
    return model.created_at.strftime("%Y-%m-%d %H:%M:%S")


def updated_at_formatter(model: type, _: Column[Any]) -> str:
    if not isinstance(model, BaseModel):
        raise TypeError("Model must be an instance of BaseModel")
    return model.updated_at.strftime("%Y-%m-%d %H:%M:%S")
