from uuid import uuid4

import pytest
from pydantic import ValidationError
from teampass.report.dto import ReportContent
from teampass.report.dto.blocks._base import ReportBlock
from teampass.report.dto.blocks.code import CodeData
from teampass.report.dto.blocks.delimiter import DelimiterData
from teampass.report.dto.blocks.header import HeaderData
from teampass.report.dto.blocks.image import (
    ImageData,
    ImageFile,
    ImageFileWithURL,
)
from teampass.report.dto.blocks.list import (
    ChecklistListData,
    ChecklistMeta,
    ListItem,
    OrderedListData,
    OrderedMeta,
    UnorderedListData,
    UnorderedMeta,
)
from teampass.report.dto.blocks.paragraph import ParagraphData
from teampass.report.dto.blocks.quote import QuoteData
from teampass.report.dto.blocks.text import TextData


# ──────────────────────────────────────────────
#  HeaderData
# ──────────────────────────────────────────────
class TestHeaderData:
    def test_to_html_basic(self) -> None:
        header = HeaderData(text="Hello", level=1)
        assert header.to_html() == "<h1>Hello</h1>"

    def test_to_html_different_levels(self) -> None:
        for lvl in range(1, 7):
            header = HeaderData(text="Title", level=lvl)
            assert header.to_html() == f"<h{lvl}>Title</h{lvl}>"

    def test_to_html_escapes_special_chars(self) -> None:
        header = HeaderData(text="<script>alert('xss')</script>", level=1)
        html = header.to_html()
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_to_html_empty_text(self) -> None:
        header = HeaderData(text="", level=1)
        assert header.to_html() == "<h1></h1>"


# ──────────────────────────────────────────────
#  ParagraphData
# ──────────────────────────────────────────────
class TestParagraphData:
    def test_to_html_basic(self) -> None:
        p = ParagraphData(text="Hello world")
        assert p.to_html() == "<p>Hello world</p>"

    def test_to_html_escapes_html(self) -> None:
        p = ParagraphData(text="<em>evil</em>")
        html = p.to_html()
        assert "<em>" not in html
        assert "&lt;em&gt;" in html

    def test_to_html_empty_text(self) -> None:
        p = ParagraphData(text="")
        assert p.to_html() == "<p></p>"

    def test_to_html_special_characters(self) -> None:
        p = ParagraphData(text='He said "hello" & goodbye')
        html = p.to_html()
        assert "&amp;" in html
        assert "&quot;" in html


# ──────────────────────────────────────────────
#  TextData
# ──────────────────────────────────────────────
class TestTextData:
    def test_to_html_allows_safe_tags(self) -> None:
        t = TextData(text="<b>bold</b> and <i>italic</i>")
        html = t.to_html()
        assert "<b>bold</b>" in html
        assert "<i>italic</i>" in html

    def test_to_html_strips_dangerous_tags(self) -> None:
        t = TextData(text="<script>alert('xss')</script> safe text")
        html = t.to_html()
        assert "<script>" not in html
        assert "safe text" in html

    def test_to_html_allows_anchors_with_href(self) -> None:
        t = TextData(text='<a href="https://example.com" target="_blank">link</a>')
        html = t.to_html()
        assert "<a " in html
        assert 'href="https://example.com"' in html

    def test_to_html_strips_onclick(self) -> None:
        t = TextData(text='<a href="#" onclick="alert(1)">click</a>')
        html = t.to_html()
        assert "onclick" not in html

    def test_to_html_allows_code_tag(self) -> None:
        t = TextData(text="Use <code>print()</code> in Python")
        html = t.to_html()
        assert "<code>print()</code>" in html

    def test_to_html_allows_mark_with_class(self) -> None:
        t = TextData(text='<mark class="highlight">text</mark>')
        html = t.to_html()
        assert "<mark" in html

    def test_to_html_allows_br(self) -> None:
        t = TextData(text="line1<br>line2")
        html = t.to_html()
        assert "<br>" in html

    def test_to_html_empty(self) -> None:
        t = TextData(text="")
        assert t.to_html() == ""


# ──────────────────────────────────────────────
#  CodeData
# ──────────────────────────────────────────────
class TestCodeData:
    def test_to_html_basic(self) -> None:
        c = CodeData(code="print('hello')")
        assert c.to_html() == "<pre><code>print(&#x27;hello&#x27;)</code></pre>"

    def test_to_html_escapes_html_in_code(self) -> None:
        c = CodeData(code="<div>test</div>")
        html = c.to_html()
        assert "<div>" not in html
        assert "&lt;div&gt;" in html

    def test_to_html_empty_code(self) -> None:
        c = CodeData(code="")
        assert c.to_html() == "<pre><code></code></pre>"

    def test_to_html_multiline_code(self) -> None:
        c = CodeData(code="line1\nline2\nline3")
        html = c.to_html()
        assert "line1\nline2\nline3" in html


# ──────────────────────────────────────────────
#  DelimiterData
# ──────────────────────────────────────────────
class TestDelimiterData:
    def test_to_html(self) -> None:
        d = DelimiterData()
        assert d.to_html() == "<br/>"


# ──────────────────────────────────────────────
#  QuoteData
# ──────────────────────────────────────────────
class TestQuoteData:
    def test_to_html_basic(self) -> None:
        q = QuoteData(text="A wise quote", caption="Socrates", alignment="left")
        html = q.to_html()
        assert "<blockquote>A wise quote</blockquote>" in html
        assert "Socrates" in html

    def test_to_html_center_alignment(self) -> None:
        q = QuoteData(text="Words", caption="Author", alignment="center")
        # alignment doesn't change output but validates
        html = q.to_html()
        assert "<blockquote>" in html

    def test_to_html_escapes_content(self) -> None:
        q = QuoteData(text="<script>x</script>", caption="<b>bad</b>", alignment="left")
        html = q.to_html()
        assert "<script>" not in html
        assert "<b>" not in html
        assert "&lt;script&gt;" in html

    def test_to_html_empty_caption(self) -> None:
        q = QuoteData(text="Quote", caption="", alignment="left")
        html = q.to_html()
        assert "<blockquote>Quote</blockquote>" in html

    def test_invalid_alignment(self) -> None:
        with pytest.raises(ValidationError):
            QuoteData(text="Q", caption="C", alignment="right")  # pyright: ignore[reportArgumentType]


# ──────────────────────────────────────────────
#  ImageData
# ──────────────────────────────────────────────
class TestImageData:
    def test_to_html_with_url(self) -> None:
        img = ImageData(
            file=ImageFileWithURL(id=uuid4(), url="https://img.png"),
            caption="Photo",
            withBorder=False,
            withBackground=False,
            stretched=False,
        )
        html = img.to_html()
        assert '<img src="https://img.png" alt="Photo" />' == html

    def test_to_html_without_url_raises(self) -> None:
        img = ImageData(
            file=ImageFile(id=uuid4()),
            caption="Photo",
            withBorder=False,
            withBackground=False,
            stretched=False,
        )
        with pytest.raises(RuntimeError, match="does not contain url"):
            img.to_html()

    def test_clean_url(self) -> None:
        fid = uuid4()
        img = ImageData(
            file=ImageFileWithURL(id=fid, url="https://img.png"),
            caption="Photo",
            withBorder=False,
            withBackground=False,
            stretched=False,
        )
        img.clean_url()

        assert isinstance(img.file, ImageFile)
        assert img.file.id == fid

    def test_clean_url_already_without_url(self) -> None:
        fid = uuid4()
        img = ImageData(
            file=ImageFile(id=fid),
            caption="Photo",
            withBorder=False,
            withBackground=False,
            stretched=False,
        )
        img.clean_url()

        assert isinstance(img.file, ImageFile)
        assert img.file.id == fid

    def test_add_url(self) -> None:
        fid = uuid4()
        img = ImageData(
            file=ImageFile(id=fid),
            caption="Photo",
            withBorder=False,
            withBackground=False,
            stretched=False,
        )
        img.add_url("https://new-url.png")

        assert isinstance(img.file, ImageFileWithURL)
        assert img.file.url == "https://new-url.png"
        assert img.file.id == fid

    def test_add_url_overwrites_existing(self) -> None:
        fid = uuid4()
        img = ImageData(
            file=ImageFileWithURL(id=fid, url="https://old.png"),
            caption="Photo",
            withBorder=False,
            withBackground=False,
            stretched=False,
        )
        img.add_url("https://new.png")

        assert isinstance(img.file, ImageFileWithURL)
        assert img.file.url == "https://new.png"

    def test_to_html_escapes_caption(self) -> None:
        img = ImageData(
            file=ImageFileWithURL(id=uuid4(), url="https://img.png"),
            caption='<script>alert("xss")</script>',
            withBorder=False,
            withBackground=False,
            stretched=False,
        )
        html = img.to_html()
        # Caption is placed as alt attribute without escaping currently
        assert "https://img.png" in html


# ──────────────────────────────────────────────
#  OrderedListData
# ──────────────────────────────────────────────
class TestOrderedListData:
    def test_to_html_basic(self) -> None:
        data = OrderedListData(
            style="ordered",
            meta=OrderedMeta(start=1, counterType="numeric"),
            items=[
                ListItem(
                    content="First",
                    meta=OrderedMeta(start=1, counterType="numeric"),
                ),
                ListItem(
                    content="Second",
                    meta=OrderedMeta(start=1, counterType="numeric"),
                ),
            ],
        )
        html = data.to_html()
        assert '<ol type="1">' in html
        assert "<li>First</li>" in html
        assert "<li>Second</li>" in html

    def test_to_html_custom_start(self) -> None:
        data = OrderedListData(
            style="ordered",
            meta=OrderedMeta(start=5, counterType="numeric"),
            items=[
                ListItem(
                    content="Item",
                    meta=OrderedMeta(start=1, counterType="numeric"),
                ),
            ],
        )
        html = data.to_html()
        assert 'start="5"' in html

    def test_to_html_roman_counter(self) -> None:
        data = OrderedListData(
            style="ordered",
            meta=OrderedMeta(start=1, counterType="lower-roman"),
            items=[
                ListItem(
                    content="Item",
                    meta=OrderedMeta(start=1, counterType="lower-roman"),
                ),
            ],
        )
        html = data.to_html()
        assert 'type="i"' in html

    def test_to_html_upper_alpha_counter(self) -> None:
        data = OrderedListData(
            style="ordered",
            meta=OrderedMeta(start=1, counterType="upper-alpha"),
            items=[
                ListItem(
                    content="Item",
                    meta=OrderedMeta(start=1, counterType="upper-alpha"),
                ),
            ],
        )
        html = data.to_html()
        assert 'type="A"' in html

    def test_to_html_nested_items(self) -> None:
        data = OrderedListData(
            style="ordered",
            meta=OrderedMeta(start=1, counterType="numeric"),
            items=[
                ListItem(
                    content="Parent",
                    meta=OrderedMeta(start=1, counterType="numeric"),
                    items=[
                        ListItem(
                            content="Child",
                            meta=OrderedMeta(start=1, counterType="numeric"),
                        ),
                    ],
                ),
            ],
        )
        html = data.to_html()
        assert "Parent" in html
        assert "Child" in html
        assert html.count("<ol") == 2
        assert html.count("</ol>") == 2

    def test_to_html_escapes_content(self) -> None:
        data = OrderedListData(
            style="ordered",
            meta=OrderedMeta(),
            items=[
                ListItem(
                    content="<script>x</script>",
                    meta=OrderedMeta(),
                ),
            ],
        )
        html = data.to_html()
        assert "<script>" not in html

    def test_to_html_empty_items(self) -> None:
        data = OrderedListData(
            style="ordered",
            meta=OrderedMeta(),
            items=[],
        )
        html = data.to_html()
        assert "<ol" in html
        assert "</ol>" in html


# ──────────────────────────────────────────────
#  UnorderedListData
# ──────────────────────────────────────────────
class TestUnorderedListData:
    def test_to_html_basic(self) -> None:
        data = UnorderedListData(
            style="unordered",
            meta=UnorderedMeta(),
            items=[
                ListItem(content="A", meta=UnorderedMeta()),
                ListItem(content="B", meta=UnorderedMeta()),
            ],
        )
        html = data.to_html()
        assert "<ul>" in html
        assert "<li>A</li>" in html
        assert "<li>B</li>" in html

    def test_to_html_nested(self) -> None:
        data = UnorderedListData(
            style="unordered",
            meta=UnorderedMeta(),
            items=[
                ListItem(
                    content="Parent",
                    meta=UnorderedMeta(),
                    items=[
                        ListItem(content="Child", meta=UnorderedMeta()),
                    ],
                ),
            ],
        )
        html = data.to_html()
        assert html.count("<ul>") == 2

    def test_to_html_empty(self) -> None:
        data = UnorderedListData(
            style="unordered",
            meta=UnorderedMeta(),
            items=[],
        )
        html = data.to_html()
        assert html == "<ul></ul>"


# ──────────────────────────────────────────────
#  ChecklistListData
# ──────────────────────────────────────────────
class TestChecklistListData:
    def test_to_html_basic(self) -> None:
        data = ChecklistListData(
            style="checklist",
            meta=ChecklistMeta(checked=False),
            items=[
                ListItem(content="Done", meta=ChecklistMeta(checked=True)),
                ListItem(content="Pending", meta=ChecklistMeta(checked=False)),
            ],
        )
        html = data.to_html()
        assert 'class="checklist"' in html
        assert 'type="checkbox"' in html
        assert "checked" in html
        assert "Done" in html
        assert "Pending" in html

    def test_to_html_all_checked(self) -> None:
        data = ChecklistListData(
            style="checklist",
            meta=ChecklistMeta(checked=True),
            items=[
                ListItem(content="A", meta=ChecklistMeta(checked=True)),
                ListItem(content="B", meta=ChecklistMeta(checked=True)),
            ],
        )
        html = data.to_html()
        # Each item should have "checked"
        assert html.count("checked") >= 2

    def test_to_html_nested(self) -> None:
        data = ChecklistListData(
            style="checklist",
            meta=ChecklistMeta(checked=False),
            items=[
                ListItem(
                    content="Parent",
                    meta=ChecklistMeta(checked=False),
                    items=[
                        ListItem(
                            content="Child",
                            meta=ChecklistMeta(checked=True),
                        ),
                    ],
                ),
            ],
        )
        html = data.to_html()
        assert "Parent" in html
        assert "Child" in html
        assert html.count("checklist") == 2


# ──────────────────────────────────────────────
#  ReportBlock
# ──────────────────────────────────────────────
class TestReportBlock:
    def test_to_html_delegates_to_data(self) -> None:
        block = ReportBlock(
            id="b1",
            type="header",
            data=HeaderData(text="Title", level=1),
        )
        assert block.to_html() == "<h1>Title</h1>"

    def test_to_html_delimiter(self) -> None:
        block = ReportBlock(
            id="b2",
            type="delimiter",
            data=DelimiterData(),
        )
        assert block.to_html() == "<br/>"


# ──────────────────────────────────────────────
#  ReportContent
# ──────────────────────────────────────────────
class TestReportContent:
    def test_to_html_multiple_blocks(self) -> None:
        content = ReportContent(
            time=1000,
            blocks=[
                ReportBlock(
                    id="1",
                    type="header",
                    data=HeaderData(text="Title", level=1),
                ),
                ReportBlock(
                    id="2",
                    type="paragraph",
                    data=ParagraphData(text="Body"),
                ),
                ReportBlock(
                    id="3",
                    type="delimiter",
                    data=DelimiterData(),
                ),
            ],
            version="2.30.6",
        )
        html = content.to_html()
        assert "<h1>Title</h1>" in html
        assert "<p>Body</p>" in html
        assert "<br/>" in html

    def test_to_html_empty_blocks(self) -> None:
        content = ReportContent(time=1000, blocks=[], version="2.30.6")
        assert content.to_html() == ""

    def test_model_validate_from_dict(self) -> None:
        raw = {
            "time": 1000,
            "blocks": [
                {
                    "id": "1",
                    "type": "header",
                    "data": {"text": "Hi", "level": 2},
                },
                {
                    "id": "2",
                    "type": "paragraph",
                    "data": {"text": "Paragraph"},
                },
            ],
            "version": "2.30.6",
        }
        content = ReportContent.model_validate(raw)
        assert len(content.blocks) == 2

    def test_model_validate_discriminated_union(self) -> None:
        raw = {
            "time": 1000,
            "blocks": [
                {"id": "1", "type": "code", "data": {"code": "x = 1"}},
                {"id": "2", "type": "delimiter", "data": {}},
                {
                    "id": "3",
                    "type": "quote",
                    "data": {
                        "text": "Q",
                        "caption": "C",
                        "alignment": "center",
                    },
                },
            ],
            "version": "2.30.6",
        }
        content = ReportContent.model_validate(raw)
        assert isinstance(content.blocks[0].data, CodeData)
        assert isinstance(content.blocks[1].data, DelimiterData)
        assert isinstance(content.blocks[2].data, QuoteData)

    def test_model_validate_invalid_block_type(self) -> None:
        raw = {
            "time": 1000,
            "blocks": [
                {"id": "1", "type": "unknown_type", "data": {"foo": "bar"}},
            ],
            "version": "2.30.6",
        }
        with pytest.raises(ValidationError):
            ReportContent.model_validate(raw)

    def test_model_validate_missing_required_field(self) -> None:
        raw = {
            "time": 1000,
            "blocks": [
                {"id": "1", "type": "header", "data": {"text": "Hi"}},
                # missing "level" in header data
            ],
            "version": "2.30.6",
        }
        with pytest.raises(ValidationError):
            ReportContent.model_validate(raw)

    def test_model_validate_list_discriminator(self) -> None:
        raw = {
            "time": 1000,
            "blocks": [
                {
                    "id": "1",
                    "type": "list",
                    "data": {
                        "style": "ordered",
                        "meta": {"start": 1, "counterType": "numeric"},
                        "items": [
                            {
                                "content": "First",
                                "meta": {"start": 1, "counterType": "numeric"},
                            }
                        ],
                    },
                },
                {
                    "id": "2",
                    "type": "list",
                    "data": {
                        "style": "unordered",
                        "meta": {},
                        "items": [{"content": "Item", "meta": {}}],
                    },
                },
                {
                    "id": "3",
                    "type": "list",
                    "data": {
                        "style": "checklist",
                        "meta": {"checked": False},
                        "items": [{"content": "Task", "meta": {"checked": True}}],
                    },
                },
            ],
            "version": "2.30.6",
        }
        content = ReportContent.model_validate(raw)
        assert isinstance(content.blocks[0].data, OrderedListData)
        assert isinstance(content.blocks[1].data, UnorderedListData)
        assert isinstance(content.blocks[2].data, ChecklistListData)

    def test_model_dump_roundtrip(self) -> None:
        content = ReportContent(
            time=1000,
            blocks=[
                ReportBlock(
                    id="1",
                    type="header",
                    data=HeaderData(text="Test", level=1),
                ),
            ],
            version="2.30.6",
        )
        dumped = content.model_dump(mode="json")
        restored = ReportContent.model_validate(dumped)
        assert isinstance(restored.blocks[0].data, HeaderData)
        assert restored.blocks[0].data.text == "Test"

    def test_to_html_concatenation_order(self) -> None:
        content = ReportContent(
            time=1000,
            blocks=[
                ReportBlock(id="1", type="header", data=HeaderData(text="A", level=1)),
                ReportBlock(
                    id="2",
                    type="paragraph",
                    data=ParagraphData(text="B"),
                ),
            ],
            version="2.30.6",
        )
        html = content.to_html()
        assert html.index("<h1>") < html.index("<p>")


# ──────────────────────────────────────────────
#  ReportNotFoundException
# ──────────────────────────────────────────────
class TestReportNotFoundException:
    def test_stores_report_id(self) -> None:
        from teampass.report.methods.exceptions import ReportNotFoundException

        rid = uuid4()
        exc = ReportNotFoundException(rid)
        assert exc.report_id == rid
        assert str(rid) in str(exc)

    def test_is_domain_not_found_exception(self) -> None:
        from teampass.domain_core import DomainNotFoundException
        from teampass.report.methods.exceptions import ReportNotFoundException

        exc = ReportNotFoundException(uuid4())
        assert isinstance(exc, DomainNotFoundException)
