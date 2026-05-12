import asyncio
from io import BytesIO
from typing import Protocol, override

import structlog
from aioboto3 import Session
from botocore.exceptions import ClientError
from dishka import Provider, Scope, provide
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from teampass.media_storage.settings import MediaStorageSettings

from . import exceptions


class IS3Client(Protocol):
    async def save_media(
        self, data: bytes, file_name: str, max_retries: int = 3
    ) -> None: ...

    async def generate_presigned_url(
        self, file_name: str, expires_seconds: int = 3600, max_retries: int = 3
    ) -> str: ...


class S3Client(IS3Client):
    def __init__(self, storage_settings: MediaStorageSettings) -> None:
        self.settings: MediaStorageSettings = storage_settings
        self.s3: Session = Session(
            aws_access_key_id=storage_settings.s3_access_key,
            aws_secret_access_key=storage_settings.s3_secret_key,
            region_name=storage_settings.s3_region_name,
        )
        self.logger: structlog.BoundLogger = structlog.get_logger("s3_client")
        self.tracer: trace.Tracer = trace.get_tracer("s3_client")

    @override
    async def save_media(
        self, data: bytes, file_name: str, max_retries: int = 3
    ) -> None:
        with self.tracer.start_as_current_span("s3_client.upload_media") as span:
            span.set_attribute(
                "s3_client.max_file_size_bytes", self.settings.max_file_size_bytes
            )
            span.set_attribute("s3_client.bucket", self.settings.s3_bucket_name)
            span.set_attribute("s3_client.operation", "upload_fileobj")
            span.set_attribute("s3_client.file_name", file_name)
            span.set_attribute("s3_client.file_size_bytes", len(data))
            file_size = len(data)
            logger = self.logger.bind(
                file_name=file_name,
                file_size_bytes=len(data),
                bucket=self.settings.s3_bucket_name,
            )

            if file_size > self.settings.max_file_size_bytes:
                logger.error(
                    "media_too_large",
                    max_size_bytes=self.settings.max_file_size_bytes,
                )
                span.set_status(Status(StatusCode.ERROR, "Media too large"))
                raise exceptions.MediaTooLargeError(
                    file_name, self.settings.max_file_size_bytes, file_size
                )

            logger.info("uploading_media", stage="start")

            for attempt in range(1, max_retries + 1):
                try:
                    async with self._get_client() as s3_client:
                        await s3_client.upload_fileobj(
                            BytesIO(data), self.settings.s3_bucket_name, file_name
                        )
                    logger.info(
                        "media_uploaded",
                        stage="complete",
                        attempt=attempt,
                    )
                    return

                except ClientError as e:
                    code = e.response.get("Error", {}).get("Code", "Unknown")
                    if code in {"AccessDenied", "NoSuchBucket"}:
                        logger.error("s3_config_error", error_code=code, exc_info=True)
                        span.set_status(
                            Status(StatusCode.ERROR, f"S3 config error: {code}")
                        )
                        span.record_exception(e)
                        raise exceptions.ConfigError(f"S3 {code}: {e}") from e

                    wait = 2 ** (attempt - 1)
                    logger.warning(
                        "upload_retry",
                        attempt=attempt,
                        max_retries=max_retries,
                        wait_seconds=wait,
                        error_code=code,
                    )
                    if attempt < max_retries:
                        await asyncio.sleep(wait)

                except Exception as e:
                    wait = 2 ** (attempt - 1)
                    logger.warning(
                        "upload_retry",
                        attempt=attempt,
                        max_retries=max_retries,
                        wait_seconds=wait,
                        error_type=type(e).__name__,
                        exc_info=True,
                    )
                    if attempt < max_retries:
                        await asyncio.sleep(wait)

            logger.error("upload_max_retries_exceeded", max_attempts=max_retries)
            span.set_status(Status(StatusCode.ERROR, "Max retries exceeded"))
            raise exceptions.MaxRetriesExceededError(max_retries)

    @override
    async def generate_presigned_url(
        self, file_name: str, expires_seconds: int = 3600, max_retries: int = 3
    ) -> str:
        with self.tracer.start_as_current_span(
            "s3_client.generate_presigned_url"
        ) as span:
            span.set_attribute("s3_client.bucket", self.settings.s3_bucket_name)
            span.set_attribute("s3_client.operation", "generate_presigned_url")
            span.set_attribute("s3_client.file_name", file_name)
            span.set_attribute("s3_client.url_expires_seconds", expires_seconds)

            logger = self.logger.bind(
                file_name=file_name,
                bucket=self.settings.s3_bucket_name,
                expires_seconds=expires_seconds,
            )

            logger.info("generating_presigned_url", stage="start")

            for attempt in range(1, max_retries + 1):
                try:
                    async with self._get_client() as s3_client:
                        try:
                            await s3_client.head_object(
                                Bucket=self.settings.s3_bucket_name, Key=file_name
                            )
                        except ClientError as head_e:
                            code = head_e.response.get("Error", {}).get("Code")
                            if code in {"404", "NoSuchKey"}:
                                logger.error("media_not_found", file_name=file_name)
                                span.set_status(
                                    Status(StatusCode.ERROR, "Media not found")
                                )
                                raise exceptions.MediaNotFoundError(
                                    file_name
                                ) from head_e
                            raise head_e

                        url = await s3_client.generate_presigned_url(
                            ClientMethod="get_object",
                            Params={
                                "Bucket": self.settings.s3_bucket_name,
                                "Key": file_name,
                            },
                            ExpiresIn=expires_seconds,
                        )

                    logger.info(
                        "presigned_url_generated",
                        stage="complete",
                        attempt=attempt,
                    )
                    return url

                except ClientError as e:
                    code = e.response.get("Error", {}).get("Code", "Unknown")
                    if code in {"AccessDenied", "NoSuchBucket"}:
                        logger.error("s3_config_error", error_code=code, exc_info=True)
                        span.set_status(
                            Status(StatusCode.ERROR, f"S3 config error: {code}")
                        )
                        span.record_exception(e)
                        raise exceptions.ConfigError(f"S3 {code}: {e}") from e
                    if code in {"404", "NoSuchKey"}:
                        logger.error("media_not_found", file_name=file_name)
                        span.set_status(Status(StatusCode.ERROR, "Media not found"))
                        raise exceptions.MediaNotFoundError(file_name) from e

                    wait = 2 ** (attempt - 1)
                    logger.warning(
                        "presigned_retry",
                        attempt=attempt,
                        max_retries=max_retries,
                        wait_seconds=wait,
                        error_code=code,
                    )
                    if attempt < max_retries:
                        await asyncio.sleep(wait)

                except exceptions.MediaNotFoundError:
                    raise

                except Exception as e:
                    wait = 2 ** (attempt - 1)
                    logger.warning(
                        "presigned_retry",
                        attempt=attempt,
                        max_retries=max_retries,
                        wait_seconds=wait,
                        error_type=type(e).__name__,
                        exc_info=True,
                    )
                    if attempt < max_retries:
                        await asyncio.sleep(wait)

            logger.error("presigned_max_retries_exceeded", max_attempts=max_retries)
            span.set_status(Status(StatusCode.ERROR, "Max retries exceeded"))
            raise exceptions.MaxRetriesExceededError(max_retries)

    def _get_client(self):
        return self.s3.client(
            service_name="s3", endpoint_url=self.settings.s3_endpoint_url
        )


class S3ClientProvider(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> MediaStorageSettings:
        return MediaStorageSettings()  # type: ignore # pyright: ignore

    @provide(scope=Scope.APP)
    def s3_client(self, settings: MediaStorageSettings) -> IS3Client:
        return S3Client(settings)
