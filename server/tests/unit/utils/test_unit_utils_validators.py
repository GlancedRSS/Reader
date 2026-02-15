"""Unit tests for validation utilities."""

from datetime import datetime, timedelta

import pytest

from backend.utils.validators import (
    validate_batch_size,
    validate_date_range,
    validate_file_size,
    validate_folder_name,
    validate_opml_filename,
    validate_url,
)


class TestValidateUrl:
    """Test URL validation."""

    async def test_validate_url_valid(self):
        """Should accept valid URLs."""
        validate_url("https://example.com")
        validate_url("http://example.com")
        validate_url("https://example.com/path?query=value")

    async def test_validate_url_empty(self):
        """Should reject empty URL."""
        with pytest.raises(ValueError, match="URL is required"):
            validate_url("")
        with pytest.raises(ValueError, match="URL is required"):
            validate_url("   ")

    async def test_validate_url_no_scheme(self):
        """Should reject URL without scheme."""
        with pytest.raises(ValueError, match="Invalid URL format"):
            validate_url("example.com")
        with pytest.raises(ValueError, match="Invalid URL format"):
            validate_url("//example.com")

    async def test_validate_url_invalid_scheme(self):
        """Should reject non-HTTP schemes."""
        # javascript: is parsed as having a scheme but no netloc, so it gets caught by the scheme check
        with pytest.raises(ValueError, match="Invalid URL format"):
            validate_url("javascript:alert('xss')")
        # ftp: is parsed as having a scheme and netloc, but scheme check happens first
        with pytest.raises(ValueError, match="Only HTTP and HTTPS"):
            validate_url("ftp://example.com")

    async def test_validate_url_localhost(self):
        """Should reject localhost URLs."""
        with pytest.raises(ValueError, match=r"Localhost.*not allowed"):
            validate_url("http://localhost")
        with pytest.raises(ValueError, match=r"Localhost.*not allowed"):
            validate_url("https://127.0.0.1")
        with pytest.raises(ValueError, match=r"Localhost.*not allowed"):
            validate_url("http://0.0.0.0")


class TestValidateDateRange:
    """Test date range validation."""

    async def test_validate_date_range_none(self):
        """Should accept None values."""
        validate_date_range(None, None)
        validate_date_range(datetime.now(), None)
        validate_date_range(None, datetime.now())

    async def test_validate_date_range_future(self):
        """Should reject future dates."""
        future = datetime.now() + timedelta(days=1)
        with pytest.raises(ValueError, match="cannot be in the future"):
            validate_date_range(future, None)
        with pytest.raises(ValueError, match="cannot be in the future"):
            validate_date_range(None, future)

    async def test_validate_date_range_inverted(self):
        """Should reject inverted range."""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        with pytest.raises(ValueError, match="Start date cannot be after end"):
            validate_date_range(now, yesterday)

    async def test_validate_date_range_too_long(self):
        """Should reject ranges longer than 1 year."""
        now = datetime.now()
        # To test the 1 year limit, need dates that are both in the past
        # but the range exceeds 365 days
        thirteen_months_ago = now - timedelta(days=400)
        ten_days_ago = now - timedelta(days=10)
        # Difference is 390 days, which exceeds 365 days (1 year)
        with pytest.raises(ValueError, match="cannot exceed 1 year"):
            validate_date_range(thirteen_months_ago, ten_days_ago)

    async def test_validate_date_range_too_old(self):
        """Should reject start dates older than 2 years."""
        now = datetime.now()
        three_years_ago = now - timedelta(days=1000)
        with pytest.raises(ValueError, match="Start date too old"):
            validate_date_range(three_years_ago, None)

    async def test_validate_date_range_valid(self):
        """Should accept valid date ranges."""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        last_week = now - timedelta(days=7)

        validate_date_range(last_week, now)
        validate_date_range(yesterday, None)


class TestValidateFolderName:
    """Test folder name validation."""

    async def test_validate_folder_name_valid(self):
        """Should accept valid folder names."""
        assert validate_folder_name("Tech") == "Tech"
        assert validate_folder_name("  News  ") == "News"
        assert validate_folder_name("My Feeds") == "My Feeds"

    async def test_validate_folder_name_empty(self):
        """Should reject empty folder name."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_folder_name("")
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_folder_name("   ")

    async def test_validate_folder_name_too_long(self):
        """Should reject folder name exceeding max length."""
        long_name = "a" * 101
        with pytest.raises(ValueError, match="too long"):
            validate_folder_name(long_name, max_length=100)

    async def test_validate_folder_name_custom_max_length(self):
        """Should respect custom max length."""
        assert validate_folder_name("abc", max_length=3) == "abc"
        long_name = "a" * 11
        with pytest.raises(ValueError, match="too long"):
            validate_folder_name(long_name, max_length=10)


class TestValidateOpmlFilename:
    """Test OPML filename validation."""

    async def test_validate_opml_filename_valid(self):
        """Should accept valid OPML filenames."""
        assert validate_opml_filename("feeds.opml") == "feeds.opml"
        assert validate_opml_filename("my-feeds.opml") == "my-feeds.opml"
        assert (
            validate_opml_filename("subscriptions.xml.opml")
            == "subscriptions.xml.opml"
        )

    async def test_validate_opml_filename_empty(self):
        """Should reject empty filename."""
        with pytest.raises(ValueError, match="No filename provided"):
            validate_opml_filename("")
        with pytest.raises(ValueError, match="No filename provided"):
            validate_opml_filename(None)

    async def test_validate_opml_filename_wrong_extension(self):
        """Should reject non-OPML files."""
        with pytest.raises(ValueError, match="Invalid file format"):
            validate_opml_filename("feeds.xml")
        with pytest.raises(ValueError, match="Invalid file format"):
            validate_opml_filename("backup.txt")

    async def test_validate_opml_filename_path_traversal(self):
        """Should reject filenames with path separators."""
        with pytest.raises(ValueError, match="Invalid filename"):
            validate_opml_filename("../feeds.opml")
        with pytest.raises(ValueError, match="Invalid filename"):
            validate_opml_filename("subdir/feeds.opml")
        with pytest.raises(ValueError, match="Invalid filename"):
            validate_opml_filename("..\\feeds.opml")


class TestValidateFileSize:
    """Test file size validation."""

    async def test_validate_file_size_valid(self):
        """Should accept files under max size."""
        validate_file_size(1024, 10 * 1024 * 1024)  # 1KB under 10MB
        validate_file_size(5 * 1024 * 1024, 10 * 1024 * 1024)  # 5MB under 10MB

    async def test_validate_file_size_too_large(self):
        """Should reject files exceeding max size."""
        with pytest.raises(
            ValueError, match=r"too large. Maximum size is 10MB"
        ):
            validate_file_size(11 * 1024 * 1024, 10 * 1024 * 1024)

    async def test_validate_file_size_custom_type(self):
        """Should use custom file type in error message."""
        with pytest.raises(ValueError, match="Image too large"):
            validate_file_size(6 * 1024 * 1024, 5 * 1024 * 1024, "Image")


class TestValidateBatchSize:
    """Test batch size validation."""

    async def test_validate_batch_size_valid(self):
        """Should accept batches under max size."""
        validate_batch_size(10, 100)
        validate_batch_size(100, 100)

    async def test_validate_batch_size_exceeds_max(self):
        """Should reject batches exceeding max size."""
        with pytest.raises(ValueError, match="exceeds maximum"):
            validate_batch_size(101, 100)
        with pytest.raises(ValueError, match="exceeds maximum"):
            validate_batch_size(50, 25)
