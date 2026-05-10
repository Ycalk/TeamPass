import uuid

import pytest
from teampass.media_storage.methods.exceptions import MediaTooLargeException
from teampass.media_storage.methods.save_media import SaveMediaCommand, SaveMediaMethod
from teampass.media_storage.s3 import IS3Client
from teampass.media_storage.settings import MediaStorageSettings
from teampass.media_storage.storage import MediaDAO
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import User


@pytest.mark.asyncio
class TestSaveMedia:
    async def test_save_media_success(
        self,
        save_media_method: SaveMediaMethod,
        media_dao: MediaDAO,
        s3_client: IS3Client,
        test_png: bytes,
        user: User,
    ) -> None:
        command = SaveMediaCommand(media_data=test_png, user_id=user.id)

        media = await save_media_method(command)

        assert media.mime_type == "image/png"
        assert media.size_bytes == len(test_png)

        db_media = await media_dao.find_by_id(media.id)
        assert db_media is not None
        assert db_media.mime_type == "image/png"
        assert db_media.file_name == f"{media.id}.png"
        assert db_media.owner_id == user.id

        url = await s3_client.generate_presigned_url(db_media.file_name)
        assert url.startswith("http")

    async def test_save_media_unknown_type(
        self,
        save_media_method: SaveMediaMethod,
        media_dao: MediaDAO,
        s3_client: IS3Client,
        user: User,
    ) -> None:
        data = b"hello random text"
        command = SaveMediaCommand(media_data=data, user_id=user.id)

        media = await save_media_method(command)

        assert media.mime_type == "application/octet-stream"

        db_media = await media_dao.find_by_id(media.id)
        assert db_media is not None
        assert db_media.file_name == f"{media.id}.bin"

        url = await s3_client.generate_presigned_url(db_media.file_name)
        assert url.startswith("http")

    async def test_save_media_too_large(
        self,
        save_media_method: SaveMediaMethod,
        media_storage_settings: MediaStorageSettings,
        user: User,
    ) -> None:
        large_data = b"0" * (media_storage_settings.max_file_size_bytes + 1)
        command = SaveMediaCommand(media_data=large_data, user_id=user.id)

        with pytest.raises(MediaTooLargeException):
            await save_media_method(command)

    async def test_save_media_user_not_found(
        self,
        save_media_method: SaveMediaMethod,
        test_png: bytes,
    ) -> None:
        command = SaveMediaCommand(media_data=test_png, user_id=uuid.uuid4())

        with pytest.raises(UserNotFoundException):
            await save_media_method(command)
