import uuid

import pytest
from dishka.entities.depends_marker import FromDishka
from teampass.media_storage.methods.exceptions import MediaNotFoundException
from teampass.media_storage.methods.get_media import GetMediaCommand, GetMediaMethod
from teampass.media_storage.methods.save_media import SaveMediaCommand, SaveMediaMethod
from teampass.media_storage.storage import MediaDAO
from teampass.user.storage import User

from development.pytest_inject import inject


@pytest.mark.asyncio
class TestGetMedia:
    @inject
    async def test_get_media_success(
        self,
        get_media_method: FromDishka[GetMediaMethod],
        save_media_method: FromDishka[SaveMediaMethod],
        test_png: bytes,
        user: User,
    ) -> None:
        save_cmd = SaveMediaCommand(media_data=test_png, user_id=user.id)
        saved_media = await save_media_method(save_cmd)

        get_cmd = GetMediaCommand(media_id=saved_media.id)
        media_with_url = await get_media_method(get_cmd)

        assert media_with_url.id == saved_media.id
        assert media_with_url.mime_type == saved_media.mime_type
        assert media_with_url.size_bytes == saved_media.size_bytes
        assert media_with_url.url.startswith("http")

    @inject
    async def test_get_media_not_found_in_db(
        self,
        get_media_method: FromDishka[GetMediaMethod],
    ) -> None:
        cmd = GetMediaCommand(media_id=uuid.uuid4())
        with pytest.raises(MediaNotFoundException):
            await get_media_method(cmd)

    @inject
    async def test_get_media_not_found_in_s3(
        self,
        get_media_method: FromDishka[GetMediaMethod],
        media_dao: FromDishka[MediaDAO],
        user: User,
    ) -> None:
        media_id = uuid.uuid4()

        # Create record in DB directly without uploading to S3
        await media_dao.create(
            mime_type="image/png",
            size_bytes=100,
            file_name=f"{media_id}.png",
            owner_id=user.id,
        )
        await media_dao.commit()

        cmd = GetMediaCommand(media_id=media_id)
        with pytest.raises(MediaNotFoundException):
            await get_media_method(cmd)
