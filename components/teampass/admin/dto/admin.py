from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel
from teampass.admin.storage import Admin as AdminPersistent


class Admin(BaseModel):
    id: UUID
    username: str
    created_at: datetime

    @classmethod
    def from_persistent(cls, persistent: AdminPersistent) -> Self:
        return cls(
            id=persistent.id,
            username=persistent.username,
            created_at=persistent.created_at,
        )
