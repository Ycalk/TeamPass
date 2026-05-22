from typing import Any
from uuid import UUID, uuid4

import pytest
from dishka.entities.depends_marker import FromDishka
from teampass.report import (
    CreateReportCommand,
    CreateReportMethod,
    GetReportCommand,
    GetReportMethod,
    ReportNotFoundException,
    UpdateReportCommand,
    UpdateReportMethod,
    UploadMediaCommand,
    UploadMediaMethod,
)
from teampass.report.dto import ReportContent
from teampass.report.dto.blocks import CodeData, DelimiterData, HeaderData, QuoteData
from teampass.report.dto.blocks.image import ImageData, ImageFile, ImageFileWithURL
from teampass.report.storage import ReportDAO
from teampass.user.methods.exceptions import UserNotFoundException
from teampass.user.storage import User

from development.pytest_inject import inject


def _make_content(*blocks: dict[str, Any]) -> ReportContent:
    return ReportContent.model_validate(
        {"time": 1000, "blocks": list(blocks), "version": "2.30.6"}
    )


def _header_block(text: str = "Hello", level: int = 1) -> dict[str, Any]:
    return {
        "id": "h1",
        "type": "header",
        "data": {"text": text, "level": level},
    }


def _paragraph_block(text: str = "Some paragraph") -> dict[str, Any]:
    return {
        "id": "p1",
        "type": "paragraph",
        "data": {"text": text},
    }


def _text_block(text: str = "<b>bold</b> plain") -> dict[str, Any]:
    return {
        "id": "t1",
        "type": "text",
        "data": {"text": text},
    }


def _code_block(code: str = "print('hi')") -> dict[str, Any]:
    return {
        "id": "c1",
        "type": "code",
        "data": {"code": code},
    }


def _delimiter_block() -> dict[str, Any]:
    return {
        "id": "d1",
        "type": "delimiter",
        "data": {},
    }


def _quote_block(
    text: str = "Quote", caption: str = "Author", alignment: str = "left"
) -> dict[str, Any]:
    return {
        "id": "q1",
        "type": "quote",
        "data": {"text": text, "caption": caption, "alignment": alignment},
    }


def _image_block(file_id: UUID | None = None, with_url: bool = False) -> dict[str, Any]:
    fid = str(file_id or uuid4())
    file_data = {"id": fid}
    if with_url:
        file_data["url"] = "https://example.com/image.png"
    return {
        "id": "img1",
        "type": "image",
        "data": {
            "file": file_data,
            "caption": "Test image",
            "withBorder": False,
            "withBackground": False,
            "stretched": False,
        },
    }


def _ordered_list_block() -> dict[str, Any]:
    return {
        "id": "ol1",
        "type": "list",
        "data": {
            "style": "ordered",
            "meta": {"start": 1, "counterType": "numeric"},
            "items": [
                {"content": "First", "meta": {"start": 1, "counterType": "numeric"}},
                {"content": "Second", "meta": {"start": 1, "counterType": "numeric"}},
            ],
        },
    }


def _unordered_list_block() -> dict[str, Any]:
    return {
        "id": "ul1",
        "type": "list",
        "data": {
            "style": "unordered",
            "meta": {},
            "items": [
                {"content": "Item A", "meta": {}},
                {"content": "Item B", "meta": {}},
            ],
        },
    }


def _checklist_block() -> dict[str, Any]:
    return {
        "id": "cl1",
        "type": "list",
        "data": {
            "style": "checklist",
            "meta": {"checked": False},
            "items": [
                {"content": "Done", "meta": {"checked": True}},
                {"content": "Pending", "meta": {"checked": False}},
            ],
        },
    }


# ──────────────────────────────────────────────
#  CreateReportMethod
# ──────────────────────────────────────────────
@pytest.mark.asyncio
class TestCreateReportMethod:
    @inject
    async def test_create_report_success(
        self,
        create_report_method: FromDishka[CreateReportMethod],
        report_dao: FromDishka[ReportDAO],
        user: User,
    ) -> None:
        content = _make_content(_header_block(), _paragraph_block())
        command = CreateReportCommand(user_id=user.id, content=content)

        report_id = await create_report_method(command)

        assert report_id is not None
        report = await report_dao.find_by_id(report_id)
        assert report is not None
        assert report.owner_id == user.id
        assert report.content is not None

    @inject
    async def test_create_report_empty_blocks(
        self,
        create_report_method: FromDishka[CreateReportMethod],
        report_dao: FromDishka[ReportDAO],
        user: User,
    ) -> None:
        content = _make_content()
        command = CreateReportCommand(user_id=user.id, content=content)

        report_id = await create_report_method(command)

        report = await report_dao.find_by_id(report_id)
        assert report is not None
        parsed = ReportContent.model_validate(report.content)
        assert parsed.blocks == []

    @inject
    async def test_create_report_user_not_found(
        self,
        create_report_method: FromDishka[CreateReportMethod],
    ) -> None:
        fake_id = uuid4()
        content = _make_content(_header_block())
        command = CreateReportCommand(user_id=fake_id, content=content)

        with pytest.raises(UserNotFoundException) as exc_info:
            await create_report_method(command)

        assert exc_info.value.user_id == fake_id

    @inject
    async def test_create_report_with_image_strips_url(
        self,
        create_report_method: FromDishka[CreateReportMethod],
        report_dao: FromDishka[ReportDAO],
        user: User,
    ) -> None:
        """Image URLs should be cleaned on create (via UpdateReportMethod)."""
        file_id = uuid4()
        content = _make_content(_image_block(file_id=file_id, with_url=True))
        command = CreateReportCommand(user_id=user.id, content=content)

        report_id = await create_report_method(command)

        report = await report_dao.find_by_id(report_id)
        assert report is not None
        parsed = ReportContent.model_validate(report.content)
        image_data = parsed.blocks[0].data
        assert isinstance(image_data, ImageData)
        # URL should be stripped during save
        assert isinstance(image_data.file, ImageFile)

    @inject
    async def test_create_report_with_all_block_types(
        self,
        create_report_method: FromDishka[CreateReportMethod],
        report_dao: FromDishka[ReportDAO],
        user: User,
    ) -> None:
        content = _make_content(
            _header_block(),
            _paragraph_block(),
            _text_block(),
            _code_block(),
            _delimiter_block(),
            _quote_block(),
            _ordered_list_block(),
            _unordered_list_block(),
            _checklist_block(),
        )
        command = CreateReportCommand(user_id=user.id, content=content)

        report_id = await create_report_method(command)

        report = await report_dao.find_by_id(report_id)
        assert report is not None
        parsed = ReportContent.model_validate(report.content)
        assert len(parsed.blocks) == 9


# ──────────────────────────────────────────────
#  GetReportMethod
# ──────────────────────────────────────────────
@pytest.mark.asyncio
class TestGetReportMethod:
    @inject
    async def test_get_report_success(
        self,
        create_report_method: FromDishka[CreateReportMethod],
        get_report_method: FromDishka[GetReportMethod],
        user: User,
    ) -> None:
        content = _make_content(_header_block("Get Test"), _paragraph_block("Body"))
        report_id = await create_report_method(
            CreateReportCommand(user_id=user.id, content=content)
        )

        result = await get_report_method(GetReportCommand(report_id=report_id))

        assert isinstance(result, ReportContent)
        assert len(result.blocks) == 2
        assert result.version == "2.30.6"

    @inject
    async def test_get_report_not_found(
        self,
        get_report_method: FromDishka[GetReportMethod],
    ) -> None:
        fake_id = uuid4()

        with pytest.raises(ReportNotFoundException) as exc_info:
            await get_report_method(GetReportCommand(report_id=fake_id))

        assert exc_info.value.report_id == fake_id

    @inject
    async def test_get_report_preserves_content(
        self,
        create_report_method: FromDishka[CreateReportMethod],
        get_report_method: FromDishka[GetReportMethod],
        user: User,
    ) -> None:
        content = _make_content(
            _header_block("Title", level=2),
            _code_block("x = 42"),
            _delimiter_block(),
            _quote_block("Wise words", "Sage", "center"),
        )
        report_id = await create_report_method(
            CreateReportCommand(user_id=user.id, content=content)
        )

        result = await get_report_method(GetReportCommand(report_id=report_id))

        assert len(result.blocks) == 4
        assert isinstance(result.blocks[0].data, HeaderData)
        assert result.blocks[0].data.text == "Title"
        assert result.blocks[0].data.level == 2

        assert isinstance(result.blocks[1].data, CodeData)
        assert result.blocks[1].data.code == "x = 42"

        assert isinstance(result.blocks[2].data, DelimiterData)

        assert isinstance(result.blocks[3].data, QuoteData)
        assert result.blocks[3].data.caption == "Sage"
        assert result.blocks[3].data.alignment == "center"

    @inject
    async def test_get_report_with_image_adds_url(
        self,
        upload_media_method: FromDishka[UploadMediaMethod],
        create_report_method: FromDishka[CreateReportMethod],
        get_report_method: FromDishka[GetReportMethod],
        test_png: bytes,
        user: User,
    ) -> None:
        """When getting a report with images, presigned URLs should be resolved."""
        media_result = await upload_media_method(
            UploadMediaCommand(media_data=test_png, user_id=user.id)
        )

        content = _make_content(_image_block(file_id=media_result.id, with_url=True))
        report_id = await create_report_method(
            CreateReportCommand(user_id=user.id, content=content)
        )

        result = await get_report_method(GetReportCommand(report_id=report_id))

        image_data = result.blocks[0].data
        assert isinstance(image_data, ImageData)
        assert isinstance(image_data.file, ImageFileWithURL)
        assert image_data.file.url.startswith("http")
        assert image_data.file.id == media_result.id


# ──────────────────────────────────────────────
#  UpdateReportMethod
# ──────────────────────────────────────────────
@pytest.mark.asyncio
class TestUpdateReportMethod:
    @inject
    async def test_update_report_success(
        self,
        create_report_method: FromDishka[CreateReportMethod],
        update_report_method: FromDishka[UpdateReportMethod],
        report_dao: FromDishka[ReportDAO],
        user: User,
    ) -> None:
        report_id = await create_report_method(
            CreateReportCommand(
                user_id=user.id,
                content=_make_content(_header_block("Before")),
            )
        )

        new_content = _make_content(
            _header_block("After"), _paragraph_block("New paragraph")
        )
        await update_report_method(
            UpdateReportCommand(report_id=report_id, content=new_content)
        )

        report = await report_dao.find_by_id(report_id)
        assert report is not None
        parsed = ReportContent.model_validate(report.content)
        assert len(parsed.blocks) == 2
        assert isinstance(parsed.blocks[0].data, HeaderData)
        assert parsed.blocks[0].data.text == "After"

    @inject
    async def test_update_report_not_found(
        self,
        update_report_method: FromDishka[UpdateReportMethod],
    ) -> None:
        fake_id = uuid4()

        with pytest.raises(ReportNotFoundException) as exc_info:
            await update_report_method(
                UpdateReportCommand(
                    report_id=fake_id,
                    content=_make_content(_header_block()),
                )
            )

        assert exc_info.value.report_id == fake_id

    @inject
    async def test_update_report_clears_to_empty(
        self,
        create_report_method: FromDishka[CreateReportMethod],
        update_report_method: FromDishka[UpdateReportMethod],
        report_dao: FromDishka[ReportDAO],
        user: User,
    ) -> None:
        report_id = await create_report_method(
            CreateReportCommand(
                user_id=user.id,
                content=_make_content(_header_block(), _paragraph_block()),
            )
        )

        await update_report_method(
            UpdateReportCommand(report_id=report_id, content=_make_content())
        )

        report = await report_dao.find_by_id(report_id)
        assert report is not None
        parsed = ReportContent.model_validate(report.content)
        assert parsed.blocks == []

    @inject
    async def test_update_report_strips_image_urls(
        self,
        create_report_method: FromDishka[CreateReportMethod],
        update_report_method: FromDishka[UpdateReportMethod],
        report_dao: FromDishka[ReportDAO],
        user: User,
    ) -> None:
        report_id = await create_report_method(
            CreateReportCommand(
                user_id=user.id,
                content=_make_content(_header_block()),
            )
        )

        file_id = uuid4()
        new_content = _make_content(_image_block(file_id=file_id, with_url=True))
        await update_report_method(
            UpdateReportCommand(report_id=report_id, content=new_content)
        )

        report = await report_dao.find_by_id(report_id)
        assert report is not None
        parsed = ReportContent.model_validate(report.content)
        image_data = parsed.blocks[0].data
        assert isinstance(image_data, ImageData)
        assert isinstance(image_data.file, ImageFile)

    @inject
    async def test_update_report_multiple_times(
        self,
        create_report_method: FromDishka[CreateReportMethod],
        update_report_method: FromDishka[UpdateReportMethod],
        report_dao: FromDishka[ReportDAO],
        user: User,
    ) -> None:
        report_id = await create_report_method(
            CreateReportCommand(
                user_id=user.id,
                content=_make_content(_header_block("V1")),
            )
        )

        for i in range(2, 5):
            await update_report_method(
                UpdateReportCommand(
                    report_id=report_id,
                    content=_make_content(_header_block(f"V{i}")),
                )
            )

        report = await report_dao.find_by_id(report_id)
        assert report is not None
        parsed = ReportContent.model_validate(report.content)
        assert isinstance(parsed.blocks[0].data, HeaderData)
        assert parsed.blocks[0].data.text == "V4"


# ──────────────────────────────────────────────
#  UploadMediaMethod
# ──────────────────────────────────────────────
@pytest.mark.asyncio
class TestUploadMediaMethod:
    @inject
    async def test_upload_media_success(
        self,
        upload_media_method: FromDishka[UploadMediaMethod],
        test_png: bytes,
        user: User,
    ) -> None:
        command = UploadMediaCommand(media_data=test_png, user_id=user.id)

        result = await upload_media_method(command)

        assert result.id is not None
        assert result.url.startswith("http")

    @inject
    async def test_upload_media_returns_image_file_with_url(
        self,
        upload_media_method: FromDishka[UploadMediaMethod],
        test_png: bytes,
        user: User,
    ) -> None:
        command = UploadMediaCommand(media_data=test_png, user_id=user.id)

        result = await upload_media_method(command)

        assert isinstance(result, ImageFileWithURL)
        assert result.url is not None
        assert len(result.url) > 0

    @inject
    async def test_upload_media_with_unknown_type(
        self,
        upload_media_method: FromDishka[UploadMediaMethod],
        user: User,
    ) -> None:
        data = b"not a real image"
        command = UploadMediaCommand(media_data=data, user_id=user.id)

        result = await upload_media_method(command)

        assert result.id is not None
        assert result.url.startswith("http")
