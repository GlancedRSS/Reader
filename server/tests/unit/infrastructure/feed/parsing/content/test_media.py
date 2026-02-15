"""Unit tests for media extraction utilities."""

from unittest.mock import MagicMock

from backend.infrastructure.feed.parsing.content.media import MediaExtractor


class TestMediaExtractorInit:
    """Test MediaExtractor initialization."""

    def test_initializes_with_image_extensions(self):
        """Should initialize with supported image extensions."""
        extractor = MediaExtractor()
        assert len(extractor.image_extensions) > 0
        assert ".jpg" in extractor.image_extensions
        assert ".png" in extractor.image_extensions


class TestExtractImageFromEntry:
    """Test image extraction from RSS/ATOM entry metadata."""

    def test_extracts_from_media_content(self):
        """Should extract image from media_content field."""
        extractor = MediaExtractor()
        entry = MagicMock()
        entry.media_content = [
            {"type": "image/jpeg", "url": "https://example.com/image.jpg"}
        ]

        result = extractor.extract_image_from_entry(entry)
        assert result == "https://example.com/image.jpg"

    def test_extracts_from_media_content_with_medium(self):
        """Should extract image from media_content using medium field."""
        extractor = MediaExtractor()
        entry = MagicMock()
        entry.media_content = [
            {"medium": "image", "url": "https://example.com/photo.png"}
        ]

        result = extractor.extract_image_from_entry(entry)
        assert result == "https://example.com/photo.png"

    def test_extracts_from_media_thumbnail(self):
        """Should extract image from media_thumbnail field."""
        extractor = MediaExtractor()
        entry = MagicMock()
        entry.media_content = None
        entry.media_thumbnail = [{"url": "https://example.com/thumb.jpg"}]

        result = extractor.extract_image_from_entry(entry)
        assert result == "https://example.com/thumb.jpg"

    def test_extracts_from_media_thumbnail_with_href(self):
        """Should extract image from media_thumbnail using href."""
        extractor = MediaExtractor()
        entry = MagicMock()
        entry.media_content = None
        entry.media_thumbnail = [{"href": "https://example.com/thumb.png"}]

        result = extractor.extract_image_from_entry(entry)
        assert result == "https://example.com/thumb.png"

    def test_extracts_from_thumbnail_dict(self):
        """Should extract image from thumbnail dict."""
        extractor = MediaExtractor()
        entry = MagicMock()
        entry.media_content = None
        entry.media_thumbnail = None
        entry.thumbnail = {"url": "https://example.com/thumbnail.jpg"}

        result = extractor.extract_image_from_entry(entry)
        assert result == "https://example.com/thumbnail.jpg"

    def test_extracts_from_thumbnail_string(self):
        """Should extract image from thumbnail string."""
        extractor = MediaExtractor()
        entry = MagicMock()
        entry.media_content = None
        entry.media_thumbnail = None
        entry.thumbnail = "https://example.com/thumbnail.png"

        result = extractor.extract_image_from_entry(entry)
        assert result == "https://example.com/thumbnail.png"

    def test_extracts_from_enclosures(self):
        """Should extract image from enclosures."""
        extractor = MediaExtractor()
        entry = MagicMock()
        entry.media_content = None
        entry.media_thumbnail = None
        entry.thumbnail = None
        entry.enclosures = [
            {"type": "image/jpeg", "href": "https://example.com/enclosure.jpg"}
        ]

        result = extractor.extract_image_from_entry(entry)
        assert result == "https://example.com/enclosure.jpg"

    def test_extracts_from_enclosure_with_url(self):
        """Should extract image from enclosure using url field."""
        extractor = MediaExtractor()
        entry = MagicMock()
        entry.media_content = None
        entry.media_thumbnail = None
        entry.thumbnail = None
        entry.enclosures = [
            {"type": "image/png", "url": "https://example.com/photo.png"}
        ]

        result = extractor.extract_image_from_entry(entry)
        assert result == "https://example.com/photo.png"

    def test_extracts_from_image_dict(self):
        """Should extract image from image dict."""
        extractor = MediaExtractor()
        entry = MagicMock()
        entry.media_content = None
        entry.media_thumbnail = None
        entry.thumbnail = None
        entry.enclosures = None
        entry.image = {"href": "https://example.com/image.jpg"}

        result = extractor.extract_image_from_entry(entry)
        assert result == "https://example.com/image.jpg"

    def test_extracts_from_image_string(self):
        """Should extract image from image string."""
        extractor = MediaExtractor()
        entry = MagicMock()
        entry.media_content = None
        entry.media_thumbnail = None
        entry.thumbnail = None
        entry.enclosures = None
        entry.image = "https://example.com/photo.png"

        result = extractor.extract_image_from_entry(entry)
        assert result == "https://example.com/photo.png"

    def test_extracts_from_links_with_rel_image(self):
        """Should extract image from links with rel='image'."""
        extractor = MediaExtractor()
        entry = MagicMock()
        entry.media_content = None
        entry.media_thumbnail = None
        entry.thumbnail = None
        entry.enclosures = None
        entry.image = None
        entry.links = [{"rel": "image", "href": "https://example.com/link.jpg"}]

        result = extractor.extract_image_from_entry(entry)
        assert result == "https://example.com/link.jpg"

    def test_extracts_from_links_with_rel_enclosure(self):
        """Should extract image from links with rel='enclosure' and image type."""
        extractor = MediaExtractor()
        entry = MagicMock()
        entry.media_content = None
        entry.media_thumbnail = None
        entry.thumbnail = None
        entry.enclosures = None
        entry.image = None
        entry.links = [
            {
                "rel": "enclosure",
                "type": "image/jpeg",
                "href": "https://example.com/enc.jpg",
            }
        ]

        result = extractor.extract_image_from_entry(entry)
        assert result == "https://example.com/enc.jpg"

    def test_returns_none_when_no_image_found(self):
        """Should return None when no image is found."""
        extractor = MediaExtractor()
        entry = MagicMock()
        entry.media_content = None
        entry.media_thumbnail = None
        entry.thumbnail = None
        entry.enclosures = None
        entry.image = None
        entry.links = None

        result = extractor.extract_image_from_entry(entry)
        assert result is None


class TestExtractImageFromSummaryDescription:
    """Test image extraction from summary and description fields."""

    def test_extracts_from_summary(self):
        """Should extract image from summary field."""
        extractor = MediaExtractor()
        entry = MagicMock()
        entry.summary = '<p>Text <img src="https://example.com/image.jpg"></p>'
        entry.description = None

        result = extractor.extract_image_from_summary_description(entry)
        assert result == "https://example.com/image.jpg"

    def test_extracts_from_description(self):
        """Should extract image from description field."""
        extractor = MediaExtractor()
        entry = MagicMock()
        entry.summary = None
        entry.description = (
            '<div><img src="https://example.com/photo.png"></div>'
        )

        result = extractor.extract_image_from_summary_description(entry)
        assert result == "https://example.com/photo.png"

    def test_prioritizes_summary_over_description(self):
        """Should check summary before description."""
        extractor = MediaExtractor()
        entry = MagicMock()
        entry.summary = '<img src="https://example.com/summary.jpg">'
        entry.description = '<img src="https://example.com/description.jpg">'

        result = extractor.extract_image_from_summary_description(entry)
        assert result == "https://example.com/summary.jpg"

    def test_returns_none_when_no_image_in_fields(self):
        """Should return None when no image found in summary or description."""
        extractor = MediaExtractor()
        entry = MagicMock()
        entry.summary = "<p>Just text, no image</p>"
        entry.description = "<div>Also just text</div>"

        result = extractor.extract_image_from_summary_description(entry)
        assert result is None

    def test_handles_empty_fields(self):
        """Should handle empty summary and description."""
        extractor = MediaExtractor()
        entry = MagicMock()
        entry.summary = ""
        entry.description = "   "

        result = extractor.extract_image_from_summary_description(entry)
        assert result is None

    def test_handles_non_string_fields(self):
        """Should handle non-string field values."""
        extractor = MediaExtractor()
        entry = MagicMock()
        entry.summary = None
        entry.description = 12345

        result = extractor.extract_image_from_summary_description(entry)
        assert result is None


class TestExtractImageFromHtml:
    """Test image extraction from HTML content."""

    def test_extracts_first_img_tag(self):
        """Should extract first image from img tag."""
        extractor = MediaExtractor()
        html = '<p>Text</p><img src="https://example.com/image.jpg"><img src="https://example.com/second.jpg">'

        result = extractor.extract_image_from_html(html)
        assert result == "https://example.com/image.jpg"

    def test_validates_image_url(self):
        """Should only return URLs with valid image extensions."""
        extractor = MediaExtractor()
        html = '<img src="https://example.com/file.pdf">'

        result = extractor.extract_image_from_html(html)
        assert result is None  # Not a valid image extension

    def test_falls_back_to_og_image(self):
        """Should fall back to Open Graph image if no img tag found."""
        extractor = MediaExtractor()
        html = '<meta property="og:image" content="https://example.com/og.jpg">'

        result = extractor.extract_image_from_html(html)
        assert result == "https://example.com/og.jpg"

    def test_prioritizes_img_tag_over_og_image(self):
        """Should prefer img tag over Open Graph image."""
        extractor = MediaExtractor()
        html = '<img src="https://example.com/img.jpg"><meta property="og:image" content="https://example.com/og.jpg">'

        result = extractor.extract_image_from_html(html)
        assert result == "https://example.com/img.jpg"

    def test_returns_none_for_empty_html(self):
        """Should return None for empty HTML."""
        extractor = MediaExtractor()
        result = extractor.extract_image_from_html("")
        assert result is None

    def test_returns_none_for_none_input(self):
        """Should return None for None input."""
        extractor = MediaExtractor()
        result = extractor.extract_image_from_html(None)
        assert result is None

    def test_returns_none_for_html_without_images(self):
        """Should return None for HTML without images."""
        extractor = MediaExtractor()
        html = "<p>Just some text content</p>"

        result = extractor.extract_image_from_html(html)
        assert result is None


class TestIsValidImageUrl:
    """Test image URL validation."""

    def test_returns_true_for_http_image_urls(self):
        """Should return True for HTTP image URLs with valid extensions."""
        extractor = MediaExtractor()
        assert (
            extractor._is_valid_image_url("http://example.com/image.jpg")
            is True
        )
        assert (
            extractor._is_valid_image_url("http://example.com/photo.png")
            is True
        )

    def test_returns_true_for_https_image_urls(self):
        """Should return True for HTTPS image URLs."""
        extractor = MediaExtractor()
        assert (
            extractor._is_valid_image_url("https://example.com/image.gif")
            is True
        )
        assert (
            extractor._is_valid_image_url("https://example.com/photo.webp")
            is True
        )

    def test_returns_false_for_non_http_protocols(self):
        """Should return False for non-HTTP protocols."""
        extractor = MediaExtractor()
        assert (
            extractor._is_valid_image_url("ftp://example.com/image.jpg")
            is False
        )
        assert (
            extractor._is_valid_image_url("data:image/gif;base64,R0lGODlh")
            is False
        )
        assert extractor._is_valid_image_url("//example.com/image.jpg") is False

    def test_returns_false_for_urls_without_image_extension(self):
        """Should return False for URLs without image extensions."""
        extractor = MediaExtractor()
        assert (
            extractor._is_valid_image_url("https://example.com/file.pdf")
            is False
        )
        assert (
            extractor._is_valid_image_url("https://example.com/page.html")
            is False
        )
        assert extractor._is_valid_image_url("https://example.com/") is False

    def test_returns_false_for_empty_string(self):
        """Should return False for empty string."""
        extractor = MediaExtractor()
        assert extractor._is_valid_image_url("") is False

    def test_returns_false_for_none(self):
        """Should return False for None input."""
        extractor = MediaExtractor()
        assert extractor._is_valid_image_url(None) is False

    def test_is_case_insensitive_for_extensions(self):
        """Should be case-insensitive for file extensions."""
        extractor = MediaExtractor()
        # The URL is lowercased before checking, so this tests the path matching
        assert (
            extractor._is_valid_image_url("https://example.com/image.JPG")
            is True
        )
        assert (
            extractor._is_valid_image_url("https://example.com/image.PNG")
            is True
        )

    def test_handles_query_parameters_in_url(self):
        """Should handle URLs with query parameters (urlparse strips them from path)."""
        extractor = MediaExtractor()
        # urlparse strips query params, so this is valid
        assert (
            extractor._is_valid_image_url(
                "https://example.com/image.jpg?size=large"
            )
            is True
        )
        assert (
            extractor._is_valid_image_url("https://example.com/image.jpg")
            is True
        )

    def test_handles_all_supported_extensions(self):
        """Should support all configured image extensions."""
        extractor = MediaExtractor()
        assert (
            extractor._is_valid_image_url("https://example.com/img.jpg") is True
        )
        assert (
            extractor._is_valid_image_url("https://example.com/img.jpeg")
            is True
        )
        assert (
            extractor._is_valid_image_url("https://example.com/img.png") is True
        )
        assert (
            extractor._is_valid_image_url("https://example.com/img.gif") is True
        )
        assert (
            extractor._is_valid_image_url("https://example.com/img.webp")
            is True
        )
        assert (
            extractor._is_valid_image_url("https://example.com/img.bmp") is True
        )
        assert (
            extractor._is_valid_image_url("https://example.com/img.svg") is True
        )
        assert (
            extractor._is_valid_image_url("https://example.com/img.ico") is True
        )
