import uuid
from typing import Final, override
from uuid import UUID

import filetype
import structlog
from opentelemetry import trace
from pydantic import BaseModel
from teampass.domain_core import DomainMethod
from teampass.media_storage.dto import Media
from teampass.media_storage.s3 import IS3Client, MediaTooLargeError
from teampass.media_storage.storage import MediaDAO
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import UserDAO

from .exceptions import MediaTooLargeException

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class SaveMediaPayload(BaseModel):
    media_data: bytes


class SaveMediaCommand(SaveMediaPayload):
    user_id: UUID


class SaveMediaMethod(DomainMethod[SaveMediaCommand, Media]):
    def __init__(
        self, s3_client: IS3Client, media_dao: MediaDAO, user_dao: UserDAO
    ) -> None:
        self.s3_client: IS3Client = s3_client
        self.media_dao: MediaDAO = media_dao
        self.user_dao: UserDAO = user_dao

    @override
    async def __call__(self, command: SaveMediaCommand) -> Media:
        with _tracer.start_as_current_span("media_storage.save_media") as span:
            span.set_attribute("user.id", str(command.user_id))
            logger = _logger.bind(
                user_id=str(command.user_id),
            )

            user = await self.user_dao.find_by_id(command.user_id)
            if user is None:
                logger.error("user_not_found")
                raise UserNotFoundException(command.user_id)

            media_id = uuid.uuid4()

            kind = filetype.guess(command.media_data)
            if kind is None:
                extension = "bin"
                mime_type = "application/octet-stream"
            else:
                extension = kind.extension
                mime_type = kind.mime

            file_name = f"{media_id}.{extension}"
            span.set_attribute("media.id", str(media_id))
            span.set_attribute("media.file_name", file_name)

            logger.info("creating_media_record_in_db")
            db_media = await self.media_dao.create(
                id=media_id,
                mime_type=mime_type,
                size_bytes=len(command.media_data),
                file_name=file_name,
                owner_id=command.user_id,
            )

            logger.info("uploading_media_to_s3")
            try:
                await self.s3_client.save_media(
                    data=command.media_data, file_name=file_name
                )
            except MediaTooLargeError as e:
                raise MediaTooLargeException(e.message)

            await self.media_dao.commit()

            return Media.from_persistent(db_media)
