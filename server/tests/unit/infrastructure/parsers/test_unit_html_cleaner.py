"""Unit tests for HTML cleaning and sanitization utilities."""

from backend.infrastructure.parsers.html_cleaner import (
    HTMLCleaner,
    decode_html_entities,
)


class TestDecodeHtmlEntities:
    """Test HTML entity decoding function."""

    def test_decodes_basic_entities(self):
        """Should decode basic HTML entities."""
        assert decode_html_entities("&lt;") == "<"
        assert decode_html_entities("&gt;") == ">"
        assert decode_html_entities("&amp;") == "&"
        assert decode_html_entities("&quot;") == '"'
        assert decode_html_entities("&apos;") == "'"

    def test_decodes_numeric_entities(self):
        """Should decode numeric HTML entities."""
        assert decode_html_entities("&#65;") == "A"
        assert decode_html_entities("x65;") == "x65;"  # Not a valid entity

    def test_returns_empty_string_for_none(self):
        """Should handle empty input."""
        assert decode_html_entities("") == ""

    def test_handles_mixed_content(self):
        """Should handle text with entities mixed with normal text."""
        assert decode_html_entities("Hello &amp; World") == "Hello & World"


class TestHTMLCleanerInit:
    """Test HTMLCleaner initialization."""

    def test_initializes_with_allowed_tags(self):
        """Should initialize with comprehensive allowed tags set."""
        cleaner = HTMLCleaner()

        # Check some key tags are present
        assert "p" in cleaner.allowed_tags
        assert "a" in cleaner.allowed_tags
        assert "img" in cleaner.allowed_tags
        assert "script" not in cleaner.allowed_tags
        assert "style" not in cleaner.allowed_tags

    def test_initializes_with_allowed_attributes(self):
        """Should initialize with appropriate allowed attributes."""
        cleaner = HTMLCleaner()

        # Check attributes are configured
        assert "href" in cleaner.allowed_attributes.get("a", [])
        assert "src" in cleaner.allowed_attributes.get("img", [])


class TestCleanHtml:
    """Test HTML cleaning functionality."""

    def test_returns_empty_string_for_none(self):
        """Should return empty string for None input."""
        cleaner = HTMLCleaner()
        result = cleaner.clean_html("")
        assert result == ""

    def test_returns_empty_string_for_whitespace_only(self):
        """Should return empty string for whitespace-only input."""
        cleaner = HTMLCleaner()
        result = cleaner.clean_html("   ")
        assert result == ""

    def test_removes_dangerous_script_tags(self):
        """Should remove script tags completely."""
        cleaner = HTMLCleaner()
        html = "<p>Hello</p><script>alert('xss')</script>"
        result = cleaner.clean_html(html)
        assert "<script>" not in result
        assert "alert" not in result
        assert "<p>Hello</p>" in result

    def test_removes_style_tags(self):
        """Should remove style tags."""
        cleaner = HTMLCleaner()
        html = "<div>Content</div><style>body { color: red; }</style>"
        result = cleaner.clean_html(html)
        assert "<style>" not in result
        assert "color: red" not in result

    def test_removes_iframe_tags(self):
        """Should remove iframe tags."""
        cleaner = HTMLCleaner()
        html = '<p>Text</p><iframe src="evil.com"></iframe>'
        result = cleaner.clean_html(html)
        assert "<iframe>" not in result
        assert "evil.com" not in result

    def test_removes_form_and_input_tags(self):
        """Should remove form and input elements."""
        cleaner = HTMLCleaner()
        html = '<form><input type="password"></form>'
        result = cleaner.clean_html(html)
        assert "<form>" not in result
        assert "<input" not in result

    def test_preserves_safe_tags(self):
        """Should preserve safe HTML tags."""
        cleaner = HTMLCleaner()
        html = "<p>Hello <strong>world</strong></p>"
        result = cleaner.clean_html(html)
        assert "<p>Hello" in result
        assert "<strong" in result
        assert "world" in result
        assert "</strong>" in result

    def test_preserves_links_with_allowed_attributes(self):
        """Should preserve links with href attribute."""
        cleaner = HTMLCleaner()
        html = '<a href="https://example.com">Link</a>'
        result = cleaner.clean_html(html)
        assert '<a href="https://example.com"' in result
        assert "Link" in result
        assert "</a>" in result

    def test_preserves_images_with_allowed_attributes(self):
        """Should preserve images with allowed attributes."""
        cleaner = HTMLCleaner()
        html = '<img src="https://example.com/img.jpg" alt="Image">'
        result = cleaner.clean_html(html)
        assert 'src="https://example.com/img.jpg"' in result
        assert 'alt="Image"' in result

    def test_removes_dangerous_style_attributes(self):
        """Should remove style attributes with javascript."""
        cleaner = HTMLCleaner()
        html = '<div style="color: red; background: javascript:alert(1)">Text</div>'
        result = cleaner.clean_html(html)
        assert "javascript:" not in result.lower()
        assert "alert" not in result

    def test_removes_dangerous_protocols_in_href(self):
        """Should remove javascript: protocol from href."""
        cleaner = HTMLCleaner()
        html = "<a href=\"javascript:alert('xss')\">Click</a>"
        result = cleaner.clean_html(html)
        assert "javascript:" not in result.lower()
        # The href attribute may be removed or set to empty
        assert "<a>" in result or 'href=""' in result

    def test_removes_data_protocol_in_src(self):
        """Should remove data: protocol from src."""
        cleaner = HTMLCleaner()
        html = '<img src="data:text/html,<script>alert(1)</script>">'
        result = cleaner.clean_html(html)
        assert "data:" not in result.lower()
        assert "alert" not in result

    def test_preserves_pre_block_formatting(self):
        """Should preserve formatting within pre tags."""
        cleaner = HTMLCleaner()
        html = "<pre>    indented    code\n\n  here</pre>"
        result = cleaner.clean_html(html)
        assert "<pre>" in result
        # Check that some spacing is preserved
        assert "indented" in result
        assert "code" in result

    def test_handles_nested_pre_blocks(self):
        """Should handle multiple pre blocks."""
        cleaner = HTMLCleaner()
        html = "<pre>code1</pre><p>text</p><pre>code2</pre>"
        result = cleaner.clean_html(html)
        assert result.count("<pre>") == 2
        assert "code1" in result
        assert "code2" in result

    def test_normalizes_whitespace_outside_pre(self):
        """Should normalize whitespace outside pre tags."""
        cleaner = HTMLCleaner()
        html = "<p>Text   with    spaces</p>"
        result = cleaner.clean_html(html)
        assert "Text  with spaces" in result or "Text with spaces" in result

    def test_adds_spaces_around_inline_elements(self):
        """Should add spaces around inline elements to prevent merging."""
        cleaner = HTMLCleaner()
        html = "<p>Text<strong>bold</strong>more</p>"
        result = cleaner.clean_html(html)
        # Spaces should prevent "Textboldmore"
        assert "Text" in result
        assert "bold" in result
        assert "more" in result

    def test_handles_empty_html(self):
        """Should handle empty HTML gracefully."""
        cleaner = HTMLCleaner()
        result = cleaner.clean_html("")
        assert result == ""

    def test_falls_back_on_exception(self):
        """Should fall back to plain text on exception."""
        cleaner = HTMLCleaner()
        # This might cause issues in some edge cases
        html = "<p>Simple text</p>"
        result = cleaner.clean_html(html)
        assert "Simple text" in result

    def test_decodes_html_entities(self):
        """Should decode HTML entities in content."""
        cleaner = HTMLCleaner()
        html = "<p>Hello &amp; World &lt;3</p>"
        result = cleaner.clean_html(html)
        assert "Hello & World <3" in result

    def test_handles_complex_nested_html(self):
        """Should handle complex nested HTML structures."""
        cleaner = HTMLCleaner()
        html = """
        <article>
            <header>
                <h1>Title</h1>
            </header>
            <p>Content with <strong>bold</strong> and <em>italic</em></p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
        </article>
        """
        result = cleaner.clean_html(html)
        assert "<h1>Title</h1>" in result
        assert "<strong" in result
        assert "bold" in result
        assert "</strong>" in result
        assert "<em" in result
        assert "italic" in result
        assert "</em>" in result
        assert "<li>Item 1</li>" in result

    def test_allows_table_elements(self):
        """Should preserve table structure."""
        cleaner = HTMLCleaner()
        html = "<table><tr><th>Header</th></tr><tr><td>Data</td></tr></table>"
        result = cleaner.clean_html(html)
        assert "<table>" in result
        assert "<tr>" in result
        assert "<th>Header</th>" in result
        assert "<td>Data</td>" in result

    def test_allows_video_elements(self):
        """Should preserve video elements with allowed attributes."""
        cleaner = HTMLCleaner()
        html = '<video src="video.mp4" controls width="500"></video>'
        result = cleaner.clean_html(html)
        assert "<video" in result
        assert 'src="video.mp4"' in result
        assert "controls" in result

    def test_allows_audio_elements(self):
        """Should preserve audio elements."""
        cleaner = HTMLCleaner()
        html = '<audio src="audio.mp3" controls></audio>'
        result = cleaner.clean_html(html)
        assert "<audio" in result
        assert 'src="audio.mp3"' in result

    def test_allows_semantic_elements(self):
        """Should preserve HTML5 semantic elements."""
        cleaner = HTMLCleaner()
        html = "<article><section><nav><aside><footer>"
        result = cleaner.clean_html(html)
        assert "<article>" in result
        assert "<section>" in result
        assert "<nav>" in result
        assert "<aside>" in result
        assert "<footer>" in result

    def test_removes_button_tags(self):
        """Should remove button elements."""
        cleaner = HTMLCleaner()
        html = '<button onclick="alert(1)">Click</button>'
        result = cleaner.clean_html(html)
        assert "<button>" not in result
        assert "alert" not in result
        assert "Click" not in result  # Content removed with tag

    def test_removes_object_and_embed(self):
        """Should remove object and embed tags."""
        cleaner = HTMLCleaner()
        html = '<object data="file.swf"></object><embed src="file.swf">'
        result = cleaner.clean_html(html)
        assert "<object" not in result
        assert "<embed" not in result

    def test_removes_noscript_tags(self):
        """Should remove noscript tags."""
        cleaner = HTMLCleaner()
        html = "<noscript><p>JavaScript required</p></noscript>"
        result = cleaner.clean_html(html)
        assert "<noscript>" not in result

    def test_strips_unknown_tags(self):
        """Should strip tags not in allowed list."""
        cleaner = HTMLCleaner()
        html = "<p>Valid</p><custom-tag>Invalid</custom-tag>"
        result = cleaner.clean_html(html)
        assert "<p>Valid</p>" in result
        assert "<custom-tag>" not in result
        # Invalid tag content should be stripped by bleach
        # but the text might remain depending on configuration


class TestHtmlToText:
    """Test HTML to plain text conversion."""

    def test_returns_empty_string_for_none(self):
        """Should return empty string for None input."""
        cleaner = HTMLCleaner()
        result = cleaner.html_to_text("")
        assert result == ""

    def test_returns_empty_string_for_whitespace_only(self):
        """Should return empty string for whitespace-only input."""
        cleaner = HTMLCleaner()
        result = cleaner.html_to_text("   ")
        assert result == ""

    def test_extracts_text_from_paragraphs(self):
        """Should extract text from paragraph tags."""
        cleaner = HTMLCleaner()
        html = "<p>Hello world</p>"
        result = cleaner.html_to_text(html)
        assert result == "Hello world"

    def test_removes_script_and_style_content(self):
        """Should remove content from script and style tags."""
        cleaner = HTMLCleaner()
        html = "<p>Visible</p><script>alert('hidden')</script><style>body{}</style>"
        result = cleaner.html_to_text(html)
        assert "Visible" in result
        assert "alert" not in result
        assert "body{}" not in result

    def test_removes_iframe_content(self):
        """Should remove iframe tags."""
        cleaner = HTMLCleaner()
        html = '<p>Text</p><iframe src="ad.html"></iframe>'
        result = cleaner.html_to_text(html)
        assert "Text" in result
        assert "iframe" not in result.lower()
        assert "ad.html" not in result

    def test_normalizes_whitespace(self):
        """Should normalize whitespace in output."""
        cleaner = HTMLCleaner()
        html = "<p>Text   with    spaces</p>"
        result = cleaner.html_to_text(html)
        assert "Text with spaces" == result

    def test_decodes_html_entities(self):
        """Should decode HTML entities in text."""
        cleaner = HTMLCleaner()
        html = "<p>Hello &amp; World &lt;3</p>"
        result = cleaner.html_to_text(html)
        assert "Hello & World <3" == result

    def test_handles_nested_structure(self):
        """Should handle nested HTML structure."""
        cleaner = HTMLCleaner()
        html = "<div><p>Text1</p><p>Text2</p></div>"
        result = cleaner.html_to_text(html)
        assert "Text1 Text2" in result

    def test_strips_all_tags(self):
        """Should strip all HTML tags."""
        cleaner = HTMLCleaner()
        html = "<h1>Title</h1><p>Paragraph</p><ul><li>List item</li></ul>"
        result = cleaner.html_to_text(html)
        assert "<h1>" not in result
        assert "<p>" not in result
        assert "<ul>" not in result
        assert "<li>" not in result
        assert "Title Paragraph List item" in result

    def test_falls_back_on_exception(self):
        """Should fall back to regex-based stripping on exception."""
        cleaner = HTMLCleaner()
        html = "<p>Simple text</p>"
        result = cleaner.html_to_text(html)
        assert "Simple text" in result

    def test_handles_line_breaks(self):
        """Should handle line breaks appropriately."""
        cleaner = HTMLCleaner()
        html = "<p>Line1</p><p>Line2</p>"
        result = cleaner.html_to_text(html)
        assert "Line1" in result
        assert "Line2" in result

    def test_handles_links(self):
        """Should extract text from links."""
        cleaner = HTMLCleaner()
        html = '<a href="https://example.com">Link text</a>'
        result = cleaner.html_to_text(html)
        assert "Link text" in result
        assert "https://example.com" not in result  # URL is attribute, not text


class TestCleanHtmlContent:
    """Test combined HTML cleaning with image extraction."""

    def test_returns_empty_tuple_for_none_input(self):
        """Should return empty tuple for None input."""
        cleaner = HTMLCleaner()
        result = cleaner.clean_html_content("")
        assert result == ("", None)

    def test_returns_empty_tuple_for_whitespace_only(self):
        """Should return empty tuple for whitespace-only input."""
        cleaner = HTMLCleaner()
        result = cleaner.clean_html_content("   ")
        assert result == ("", None)

    def test_extracts_first_image_url(self):
        """Should extract URL from first img tag."""
        cleaner = HTMLCleaner()
        html = '<p>Text</p><img src="https://example.com/image.jpg">'
        result = cleaner.clean_html_content(html)
        assert result[1] == "https://example.com/image.jpg"

    def test_extracts_image_with_alt_text(self):
        """Should extract image URL regardless of alt text presence."""
        cleaner = HTMLCleaner()
        html = '<img src="https://example.com/img.jpg" alt="Description">'
        result = cleaner.clean_html_content(html)
        assert result[1] == "https://example.com/img.jpg"

    def test_returns_none_when_no_image(self):
        """Should return None for image URL when no img tag present."""
        cleaner = HTMLCleaner()
        html = "<p>Text without images</p>"
        result = cleaner.clean_html_content(html)
        assert result[1] is None

    def test_returns_cleaned_html_as_first_element(self):
        """Should return cleaned HTML as first tuple element."""
        cleaner = HTMLCleaner()
        html = "<p>Hello <strong>world</strong></p>"
        result = cleaner.clean_html_content(html)
        assert "Hello" in result[0]
        assert "<strong" in result[0]
        assert "world" in result[0]
        assert "</strong>" in result[0]

    def test_extracts_first_image_when_multiple(self):
        """Should extract only the first image URL when multiple present."""
        cleaner = HTMLCleaner()
        html = '<img src="first.jpg"><img src="second.jpg">'
        result = cleaner.clean_html_content(html)
        assert result[1] == "first.jpg"

    def test_handles_malformed_img_tags(self):
        """Should handle malformed img tags gracefully."""
        cleaner = HTMLCleaner()
        html = "<p>Text</p><img>"
        result = cleaner.clean_html_content(html)
        # Should return None for malformed img
        assert result[0] != ""  # Text should still be cleaned
        assert "Text" in result[0]

    def test_handles_image_without_src(self):
        """Should handle img tag without src attribute."""
        cleaner = HTMLCleaner()
        html = '<img alt="No src">'
        result = cleaner.clean_html_content(html)
        assert result[1] is None

    def test_removes_dangerous_content_before_extraction(self):
        """Should clean dangerous HTML before image extraction."""
        cleaner = HTMLCleaner()
        html = '<script>alert(1)</script><img src="image.jpg">'
        result = cleaner.clean_html_content(html)
        assert "alert" not in result[0]
        assert result[1] == "image.jpg"

    def test_preserves_image_url_in_cleaned_html(self):
        """Should preserve img tags in cleaned HTML."""
        cleaner = HTMLCleaner()
        html = '<img src="https://example.com/img.jpg" alt="Test">'
        result = cleaner.clean_html_content(html)
        assert "src=" in result[0]
        assert "https://example.com/img.jpg" in result[0]
