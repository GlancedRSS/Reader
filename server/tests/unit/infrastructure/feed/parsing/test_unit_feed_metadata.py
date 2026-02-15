"""Unit tests for feed metadata extraction."""

from unittest.mock import MagicMock

from backend.infrastructure.feed.parsing.feed_metadata import FeedExtractor


class TestDetectFeedType:
    """Test feed type detection."""

    def test_detects_atom_feed(self):
        """Should detect Atom feed from version."""
        feed = MagicMock()
        feed.version = "atom"

        result = FeedExtractor.detect_feed_type(feed)

        assert result == "atom"

    def test_detects_rss_feed(self):
        """Should detect RSS feed from version."""
        feed = MagicMock()
        feed.version = "rss"

        result = FeedExtractor.detect_feed_type(feed)

        assert result == "rss"

    def test_detects_rdf_feed(self):
        """Should detect RDF feed from version."""
        feed = MagicMock()
        feed.version = "rdf"

        result = FeedExtractor.detect_feed_type(feed)

        assert result == "rdf"

    def test_defaults_to_rss_when_no_version(self):
        """Should default to RSS when version is missing."""
        feed = MagicMock()
        feed.version = None

        result = FeedExtractor.detect_feed_type(feed)

        assert result == "rss"

    def test_detects_case_insensitive(self):
        """Should be case-insensitive for version string."""
        feed = MagicMock()
        feed.version = "ATOM"

        result = FeedExtractor.detect_feed_type(feed)

        assert result == "atom"


class TestExtractTitle:
    """Test feed title extraction."""

    def test_extracts_title(self):
        """Should extract feed title."""
        feed = MagicMock()
        feed.feed.get.return_value = "Test Feed"

        result = FeedExtractor.extract_title(feed)

        assert result == "Test Feed"

    def test_returns_empty_string_when_no_title(self):
        """Should return empty string when title is missing."""
        feed = MagicMock()
        feed.feed.get.return_value = None

        result = FeedExtractor.extract_title(feed)

        assert result == ""

    def test_returns_empty_string_for_empty_title(self):
        """Should return empty string for empty title."""
        feed = MagicMock()
        feed.feed.get.return_value = ""

        result = FeedExtractor.extract_title(feed)

        assert result == ""


class TestExtractDescription:
    """Test feed description extraction."""

    def test_extracts_short_description(self):
        """Should extract description under 500 chars."""
        feed = MagicMock()
        short_desc = "A short description"
        feed.feed.get.return_value = short_desc

        result = FeedExtractor.extract_description(feed)

        assert result == short_desc

    def test_returns_none_for_long_description(self):
        """Should return None for descriptions over 500 chars."""
        feed = MagicMock()
        long_desc = "x" * 501
        feed.feed.get.return_value = long_desc

        result = FeedExtractor.extract_description(feed)

        assert result is None

    def test_returns_none_for_empty_description(self):
        """Should return None for empty description."""
        feed = MagicMock()
        feed.feed.get.return_value = ""

        result = FeedExtractor.extract_description(feed)

        assert result is None

    def test_trims_whitespace_from_description(self):
        """Should trim whitespace from description."""
        feed = MagicMock()
        feed.feed.get.return_value = "  Description with spaces  "

        result = FeedExtractor.extract_description(feed)

        assert result == "Description with spaces"


class TestExtractLanguage:
    """Test feed language extraction."""

    def test_extracts_rss_language(self):
        """Should extract RSS language tag."""
        feed = MagicMock()
        feed.feed.language = "en"
        feed.feed = MagicMock()
        feed.feed.language = "en"

        result = FeedExtractor.extract_language(feed)

        assert result == "en"

    def test_normalizes_language_code(self):
        """Should normalize language code."""
        feed = MagicMock()
        feed.feed = MagicMock()
        feed.feed.language = "en-us"

        result = FeedExtractor.extract_language(feed)

        assert result == "en-US"

    def test_extracts_dublin_core_language(self):
        """Should extract Dublin Core language tag."""
        feed = MagicMock()
        feed.feed = MagicMock()
        feed.feed.language = None
        feed.feed.dc_language = "fr"

        result = FeedExtractor.extract_language(feed)

        assert result == "fr"

    def test_returns_none_when_no_language(self):
        """Should return None when no language found."""
        feed = MagicMock()
        feed.feed = type("Feed", (), {"language": None})()

        result = FeedExtractor.extract_language(feed)

        assert result is None


class TestNormalizeLanguageCode:
    """Test language code normalization."""

    def test_normalizes_lowercase_language_uppercase_country(self):
        """Should normalize to lowercase language, uppercase country."""
        result = FeedExtractor._normalize_language_code("en-gb")

        assert result == "en-GB"

    def test_normalizes_all_uppercase(self):
        """Should normalize all-uppercase codes."""
        result = FeedExtractor._normalize_language_code("EN-GB")

        assert result == "en-GB"

    def test_handles_language_only(self):
        """Should handle language code without country."""
        result = FeedExtractor._normalize_language_code("en")

        assert result == "en"

    def test_truncates_long_codes(self):
        """Should truncate language and country to 2 chars each."""
        result = FeedExtractor._normalize_language_code("english-GBR")

        assert result == "en-GB"

    def test_returns_empty_for_empty_input(self):
        """Should handle empty input."""
        result = FeedExtractor._normalize_language_code("")

        assert result == ""


class TestExtractWebsite:
    """Test feed website extraction."""

    def test_extracts_link_from_feed(self):
        """Should extract link from feed.link field."""
        feed = MagicMock()
        feed.feed = MagicMock()
        feed.feed.link = "https://example.com"

        result = FeedExtractor.extract_website(feed)

        assert result == "https://example.com"

    def test_extracts_alternate_link(self):
        """Should extract alternate link from links list."""
        feed = MagicMock()
        feed.feed = MagicMock()
        feed.feed.link = None
        mock_link = MagicMock()
        mock_link.rel = "alternate"
        mock_link.href = "https://example.com/page"
        feed.feed.links = [mock_link]

        result = FeedExtractor.extract_website(feed)

        assert result == "https://example.com/page"

    def test_returns_none_when_no_website(self):
        """Should return None when no website found."""
        feed = MagicMock()
        feed.feed = MagicMock()
        feed.feed.link = None
        feed.feed.links = None

        result = FeedExtractor.extract_website(feed)

        assert result is None


class TestExtractFeedMetadata:
    """Test complete feed metadata extraction."""

    def test_extracts_all_metadata(self):
        """Should extract all feed metadata."""
        feed = MagicMock()
        feed.feed.get.return_value = "Test Feed"

        result = FeedExtractor.extract_feed_metadata(feed)

        assert result["title"] == "Test Feed"
        assert "description" in result
        assert "language" in result
        assert "feed_type" in result


class TestValidateFeedStructure:
    """Test feed structure validation."""

    def test_returns_true_for_valid_feed(self):
        """Should return True for valid feed structure."""
        feed = MagicMock()
        feed.feed = MagicMock()
        feed.entries = [MagicMock()]

        is_valid, error = FeedExtractor.validate_feed_structure(feed)

        assert is_valid is True
        assert error is None

    def test_returns_false_for_no_feed_data(self):
        """Should return False when feed has no data."""
        feed = MagicMock()
        feed.feed = None

        is_valid, error = FeedExtractor.validate_feed_structure(feed)

        assert is_valid is False
        assert error == "no_feed_data"

    def test_returns_false_for_no_entries(self):
        """Should return False when feed has no entries."""
        feed = MagicMock()
        feed.feed = MagicMock()
        feed.entries = []

        is_valid, error = FeedExtractor.validate_feed_structure(feed)

        assert is_valid is False
        assert error == "no_entries"


class TestCheckBozoFlags:
    """Test feedparser bozo flag checking."""

    def test_returns_true_for_bozo_feed(self):
        """Should return True when feed has bozo flag."""
        feed = MagicMock()
        feed.bozo = True
        feed.bozo_exception = Exception("Parse error")

        has_errors, error_msg = FeedExtractor.check_bozo_flags(feed)

        assert has_errors is True
        assert error_msg == "parsing_error"

    def test_returns_false_for_clean_feed(self):
        """Should return False for clean feed."""
        feed = MagicMock()
        feed.bozo = False

        has_errors, error_msg = FeedExtractor.check_bozo_flags(feed)

        assert has_errors is False
        assert error_msg is None

    def test_returns_false_when_no_exception(self):
        """Should return False when bozo is True but no exception."""
        feed = MagicMock()
        feed.bozo = True
        feed.bozo_exception = None

        has_errors, error_msg = FeedExtractor.check_bozo_flags(feed)

        assert has_errors is False
        assert error_msg is None
