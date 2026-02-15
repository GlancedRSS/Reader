"""Unit tests for date parsing utilities."""

from datetime import UTC, timedelta

from backend.utils.date_utils import parse_iso_datetime


class TestParseIsoDatetime:
    """Test ISO 8601 datetime parsing."""

    async def test_parse_iso_datetime_with_z_suffix(self):
        """Should parse datetime with Z suffix (UTC indicator)."""
        result = parse_iso_datetime("2024-01-15T10:30:00Z")

        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30
        assert result.tzinfo == UTC

    async def test_parse_iso_datetime_with_offset(self):
        """Should parse datetime with timezone offset."""
        result = parse_iso_datetime("2024-01-15T10:30:00+00:00")

        assert result is not None
        assert result.tzinfo == UTC

    async def test_parse_iso_datetime_with_negative_offset(self):
        """Should parse datetime with negative timezone offset."""
        result = parse_iso_datetime("2024-01-15T10:30:00-05:00")

        assert result is not None
        # Should convert to UTC
        assert result.hour == 15  # 10:30 -5:00 = 15:30 UTC

    async def test_parse_iso_datetime_without_timezone(self):
        """Should treat naive datetime as UTC."""
        result = parse_iso_datetime("2024-01-15T10:30:00")

        assert result is not None
        assert result.tzinfo == UTC

    async def test_parse_iso_datetime_with_microseconds(self):
        """Should parse datetime with microseconds."""
        result = parse_iso_datetime("2024-01-15T10:30:00.123456Z")

        assert result is not None
        assert result.microsecond == 123456

    async def test_parse_iso_datetime_none(self):
        """Should return None for None input."""
        assert parse_iso_datetime(None) is None

    async def test_parse_iso_datetime_empty(self):
        """Should return None for empty string."""
        assert parse_iso_datetime("") is None

    async def test_parse_iso_datetime_invalid(self):
        """Should return None for invalid datetime string."""
        assert parse_iso_datetime("not-a-datetime") is None
        # Date-only strings are actually parsed by fromisoformat (date becomes datetime at midnight)
        # So this test needs adjustment
        assert parse_iso_datetime("invalid-date") is None

    async def test_parse_iso_datetime_various_formats(self):
        """Should handle various ISO 8601 formats."""
        # With milliseconds
        result = parse_iso_datetime("2024-01-15T10:30:00.123Z")
        assert result is not None
        assert result.microsecond == 123000

        # Different offset format
        result = parse_iso_datetime("2024-01-15T10:30:00+0000")
        assert result is not None

    async def test_parse_iso_datetime_preserves_utc(self):
        """Should preserve UTC timezone."""
        result = parse_iso_datetime("2024-01-15T10:30:00Z")

        assert result is not None
        assert result.tzinfo == UTC
        # Verify it's actually UTC
        assert result.utcoffset() == timedelta(0)
