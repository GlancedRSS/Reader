"""Unit tests for media utilities."""

from unittest.mock import MagicMock, patch

from backend.utils.media_utils import (
    IMAGE_EXTENSIONS,
    detect_feed_type,
    is_valid_image_url,
    validate_logo_url,
)


class TestValidateLogoUrl:
    """Test logo URL validation."""

    def test_returns_false_for_none_or_empty(self):
        """Should return False for None or empty string."""
        assert validate_logo_url(None) is False
        assert validate_logo_url("") is False

    def test_returns_false_for_non_string(self):
        """Should return False for non-string input."""
        assert validate_logo_url(123) is False
        assert validate_logo_url([]) is False

    def test_returns_false_for_url_without_scheme(self):
        """Should return False for URL without scheme."""
        assert validate_logo_url("example.com/image.png") is False
        assert validate_logo_url("//example.com/image.png") is False

    def test_returns_false_for_url_without_netloc(self):
        """Should return False for URL without netloc."""
        assert validate_logo_url("http:///image.png") is False

    def test_returns_true_for_valid_image_url(self):
        """Should return True for valid image URLs."""
        assert validate_logo_url("https://example.com/logo.png") is True
        assert (
            validate_logo_url("http://cdn.example.com/images/logo.jpg") is True
        )

    def test_returns_true_for_urls_without_path(self):
        """Should return True for URLs without path."""
        assert validate_logo_url("https://example.com") is True

    def test_returns_true_for_image_urls_with_query_params(self):
        """Should return True for image URLs with query parameters."""
        # Image extension should still be recognized with query params
        assert (
            validate_logo_url("https://cdn.com/img.jpg?v=1&size=small") is True
        )
        assert (
            validate_logo_url("https://example.com/logo.png?type=png") is True
        )

    def test_returns_false_for_non_image_urls_with_query_params(self):
        """Should return False for non-image URLs even with query params."""
        # Non-image extensions should return False even with query params
        assert validate_logo_url("https://example.com/logo?type=png") is False
        assert validate_logo_url("https://example.com/file.html?v=1") is False

    def test_returns_true_for_all_image_extensions(self):
        """Should return True for all supported image extensions."""
        for ext in IMAGE_EXTENSIONS:
            url = f"https://example.com/logo{ext}"
            assert validate_logo_url(url) is True

    def test_returns_false_for_urls_with_unsupported_extensions(self):
        """Should return False for URLs with unsupported extensions."""
        assert validate_logo_url("https://example.com/file.pdf") is False
        assert validate_logo_url("https://example.com/doc.html") is False

    def test_returns_false_for_malformed_url(self):
        """Should return False for malformed URL that raises exception."""
        # Create a URL that will cause urlparse to fail
        with patch("backend.utils.media_utils.urlparse") as mock_parse:
            mock_parse.side_effect = Exception("Parse error")
            assert validate_logo_url("bad://url") is False


class TestIsValidImageUrl:
    """Test valid image URL check."""

    def test_returns_false_for_none_or_empty(self):
        """Should return False for None or empty string."""
        assert is_valid_image_url(None) is False
        assert is_valid_image_url("") is False

    def test_returns_false_for_non_http_urls(self):
        """Should return False for URLs without http/https scheme."""
        assert is_valid_image_url("ftp://example.com/image.png") is False
        assert is_valid_image_url("data:image/png;base64,abc") is False

    def test_returns_true_for_image_urls(self):
        """Should return True for valid image URLs."""
        assert is_valid_image_url("https://example.com/logo.png") is True
        assert (
            is_valid_image_url("http://cdn.example.com/images/logo.jpg") is True
        )
        assert is_valid_image_url("https://example.com/photo.gif") is True
        assert is_valid_image_url("https://example.com/pic.webp") is True

    def test_returns_false_for_non_image_urls(self):
        """Should return False for URLs without image extensions."""
        assert is_valid_image_url("https://example.com/page.html") is False
        assert is_valid_image_url("https://example.com/file.pdf") is False
        assert is_valid_image_url("https://example.com/") is False

    def test_is_case_insensitive_for_extension(self):
        """Should be case insensitive for extension check."""
        assert is_valid_image_url("https://example.com/logo.PNG") is True
        assert is_valid_image_url("https://example.com/pic.JpEg") is True


class TestDetectFeedType:
    """Test feed type detection."""

    def test_returns_default_rss_when_no_version(self):
        """Should return 'rss' when feed has no version attribute."""
        mock_feed = {}
        assert detect_feed_type(mock_feed) == "rss"

    def test_detects_atom_feed(self):
        """Should detect Atom feed type."""
        mock_feed = MagicMock()
        mock_feed.version = "atom"
        assert detect_feed_type(mock_feed) == "atom"

    def test_detects_rdf_feed(self):
        """Should detect RDF feed type."""
        mock_feed = MagicMock()
        mock_feed.version = "rdf"
        assert detect_feed_type(mock_feed) == "rdf"

    def test_detects_rss_feed(self):
        """Should detect RSS feed type."""
        mock_feed = MagicMock()
        mock_feed.version = "rss"
        assert detect_feed_type(mock_feed) == "rss"

    def test_detects_atom_with_version_string(self):
        """Should detect Atom in version string."""
        mock_feed = MagicMock()
        mock_feed.version = "atom10"
        assert detect_feed_type(mock_feed) == "atom"

    def test_returns_rss_for_unknown_version(self):
        """Should return 'rss' for unknown version strings."""
        mock_feed = MagicMock()
        mock_feed.version = "unknown1.0"
        assert detect_feed_type(mock_feed) == "rss"
