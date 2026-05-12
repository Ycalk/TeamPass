from typing import Final, override
from uuid import UUID

import structlog
from opentelemetry import trace
from pydantic import BaseModel
from teampass.domain_core import DomainMethod
from teampass.media_storage.dto import Media, MediaWithPresignedUrl
from teampass.media_storage.s3 import IS3Client, MediaNotFoundError
from teampass.media_storage.storage import MediaDAO

from .exceptions import MediaNotFoundException

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class GetMediaCommand(BaseModel):
    media_id: UUID


class GetMediaMethod(DomainMethod[GetMediaCommand, MediaWithPresignedUrl]):
    def __init__(
        self,
        s3_client: IS3Client,
        media_dao: MediaDAO,
    ) -> None:
        self.s3_client: IS3Client = s3_client
        self.media_dao: MediaDAO = media_dao

    @override
    async def __call__(self, command: GetMediaCommand) -> MediaWithPresignedUrl:
        with _tracer.start_as_current_span("media_storage.get_media") as span:
            span.set_attribute("media.id", str(command.media_id))
            logger = _logger.bind(media_id=str(command.media_id))

            logger.info("fetching_media_record_from_db")
            db_media = await self.media_dao.find_by_id(command.media_id)
            if db_media is None:
                logger.error("media_record_not_found")
                raise MediaNotFoundException(
                    f"Media record with ID {command.media_id} not found"
                )

            span.set_attribute("media.file_name", db_media.file_name)

            logger.info("generating_presigned_url")
            try:
                url = await self.s3_client.generate_presigned_url(
                    file_name=db_media.file_name
                )
            except MediaNotFoundError as e:
                logger.error("media_not_found_in_s3", file_name=db_media.file_name)
                raise MediaNotFoundException(e.message) from e

            return MediaWithPresignedUrl(
                url=url, **Media.from_persistent(db_media).model_dump()
            )
