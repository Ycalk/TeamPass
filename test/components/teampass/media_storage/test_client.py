import uuid

import pytest
from dishka.entities.depends_marker import FromDishka
from teampass.media_storage.s3 import IS3Client, MediaNotFoundError, MediaTooLargeError
from teampass.media_storage.settings import MediaStorageSettings

from development.pytest_inject import inject


@pytest.mark.asyncio
class TestS3Client:
    _test_media: tuple[bytes, str] = (b"test_content", f"test_{uuid.uuid4()}.txt")

    @inject
    async def test_save_media(self, s3_client: FromDishka[IS3Client]) -> None:
        data, file_name = self._test_media
        await s3_client.save_media(data, file_name)

    @inject
    async def test_save_too_large_media(
        self,
        s3_client: FromDishka[IS3Client],
        media_storage_settings: FromDishka[MediaStorageSettings],
    ) -> None:
        large_data = b"0" * (media_storage_settings.max_file_size_bytes + 1)
        file_name = f"large_{uuid.uuid4()}.txt"
        with pytest.raises(MediaTooLargeError):
            await s3_client.save_media(large_data, file_name)

    @inject
    async def test_generate_presigned_url(
        self, s3_client: FromDishka[IS3Client]
    ) -> None:
        _, file_name = self._test_media
        url = await s3_client.generate_presigned_url(file_name)
        assert isinstance(url, str)
        assert url.startswith("http")

    @inject
    async def test_generate_presigned_url_not_found(
        self, s3_client: FromDishka[IS3Client]
    ) -> None:
        file_name = f"not_found_{uuid.uuid4()}.txt"
        with pytest.raises(MediaNotFoundError):
            await s3_client.generate_presigned_url(file_name)
