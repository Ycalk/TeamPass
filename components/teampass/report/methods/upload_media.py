from typing import Final, override
from uuid import UUID

import structlog
from opentelemetry import trace
from pydantic import BaseModel
from teampass.domain_core import DomainMethod
from teampass.media_storage.methods import (
    GetMediaCommand,
    GetMediaMethod,
    SaveMediaCommand,
    SaveMediaMethod,
)
from teampass.report.dto.blocks.image import ImageFileWithURL

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class UploadMediaCommand(BaseModel):
    media_data: bytes
    user_id: UUID


class UploadMediaMethod(DomainMethod[UploadMediaCommand, ImageFileWithURL]):
    def __init__(
        self,
        save_media: SaveMediaMethod,
        get_media: GetMediaMethod,
    ) -> None:
        self.save_media: SaveMediaMethod = save_media
        self.get_media: GetMediaMethod = get_media

    @override
    async def __call__(self, command: UploadMediaCommand) -> ImageFileWithURL:
        with _tracer.start_as_current_span("report.upload_media") as span:
            span.set_attribute("user.id", str(command.user_id))
            logger = _logger.bind(user_id=str(command.user_id))

            logger.info("uploading_report_media")

            media = await self.save_media(
                SaveMediaCommand(
                    user_id=command.user_id,
                    media_data=command.media_data,
                )
            )

            span.set_attribute("media.id", str(media.id))

            media_with_url = await self.get_media(GetMediaCommand(media_id=media.id))

            logger.info("report_media_uploaded", media_id=str(media.id))

            return ImageFileWithURL(id=media.id, url=media_with_url.url)
