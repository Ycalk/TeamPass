from typing import Self
from uuid import UUID

from pydantic import BaseModel

from .storage import Media as MediaPersistence


class Media(BaseModel):
    id: UUID
    mime_type: str
    size_bytes: int
    file_name: str

    @classmethod
    def from_persistent(cls, media: MediaPersistence) -> Self:
        return cls(
            id=media.id,
            mime_type=media.mime_type,
            size_bytes=media.size_bytes,
            file_name=media.file_name,
        )


class MediaWithPresignedUrl(Media):
    url: str
