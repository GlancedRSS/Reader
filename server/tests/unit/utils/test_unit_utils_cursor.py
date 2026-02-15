"""Unit tests for cursor pagination utilities."""

from datetime import UTC, datetime
from uuid import uuid4

from backend.utils.cursor import (
    create_article_cursor_data,
    create_feed_cursor_data,
    create_search_cursor_data,
    encode_cursor_data,
    parse_cursor_data,
)


class TestEncodeCursorData:
    """Test cursor data encoding."""

    async def test_encode_cursor_data_basic(self):
        """Should encode cursor data to base64."""
        data = {"id": "123", "timestamp": "2024-01-01T00:00:00Z"}
        encoded = encode_cursor_data(data)

        assert isinstance(encoded, str)
        assert len(encoded) > 0
        # Should be base64 (alphanumeric + +/ =)
        assert all(c.isalnum() or c in "+/=" for c in encoded)

    async def test_encode_cursor_data_complex(self):
        """Should encode complex nested data."""
        data = {
            "article_id": str(uuid4()),
            "timestamp": "2024-01-01T00:00:00Z",
            "is_published": True,
            "nested": {"key": "value"},
        }
        encoded = encode_cursor_data(data)
        assert isinstance(encoded, str)


class TestParseCursorData:
    """Test cursor data parsing."""

    async def test_parse_cursor_data_valid(self):
        """Should parse valid cursor data."""
        data = {"id": "123", "timestamp": "2024-01-01T00:00:00Z"}
        encoded = encode_cursor_data(data)
        decoded = parse_cursor_data(encoded)

        assert decoded == data
        assert decoded["id"] == "123"
        assert decoded["timestamp"] == "2024-01-01T00:00:00Z"

    async def test_parse_cursor_data_none(self):
        """Should return None for empty cursor."""
        assert parse_cursor_data(None) is None
        assert parse_cursor_data("") is None

    async def test_parse_cursor_data_invalid_base64(self):
        """Should return None for invalid base64."""
        assert parse_cursor_data("not-valid-base64!!!") is None
        assert parse_cursor_data("abc$%^&*") is None

    async def test_parse_cursor_data_invalid_json(self):
        """Should return None for invalid JSON in cursor."""
        # Valid base64 but not JSON
        import base64

        invalid_json = base64.b64encode(b"not-json").decode("utf-8")
        assert parse_cursor_data(invalid_json) is None


class TestCreateArticleCursorData:
    """Test article cursor data creation."""

    async def test_create_article_cursor_with_published_at(self):
        """Should create cursor data with published timestamp."""
        article_id = uuid4()
        published_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        created_at = datetime(2024, 1, 2, 12, 0, 0, tzinfo=UTC)

        cursor_data = create_article_cursor_data(
            article_id, published_at, created_at
        )

        assert cursor_data["timestamp"] == "2024-01-01T12:00:00+00:00"
        assert cursor_data["is_published_at"] is True
        assert cursor_data["article_id"] == str(article_id)

    async def test_create_article_cursor_without_published_at(self):
        """Should use created_at when published_at is None."""
        article_id = uuid4()
        published_at = None
        created_at = datetime(2024, 1, 2, 12, 0, 0, tzinfo=UTC)

        cursor_data = create_article_cursor_data(
            article_id, published_at, created_at
        )

        assert cursor_data["timestamp"] == "2024-01-02T12:00:00+00:00"
        assert cursor_data["is_published_at"] is False
        assert cursor_data["article_id"] == str(article_id)


class TestCreateFeedCursorData:
    """Test feed cursor data creation."""

    async def test_create_feed_cursor_with_last_update(self):
        """Should create cursor data with last update timestamp."""
        feed_id = uuid4()
        last_update = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)

        cursor_data = create_feed_cursor_data(feed_id, last_update)

        assert cursor_data["last_update"] == "2024-01-01T12:00:00+00:00"
        assert cursor_data["user_feed_id"] == str(feed_id)

    async def test_create_feed_cursor_without_last_update(self):
        """Should create cursor data with None last update."""
        feed_id = uuid4()
        last_update = None

        cursor_data = create_feed_cursor_data(feed_id, last_update)

        assert cursor_data["last_update"] is None
        assert cursor_data["user_feed_id"] == str(feed_id)


class TestCreateSearchCursorData:
    """Test search cursor data creation."""

    async def test_create_search_cursor_with_published_at(self):
        """Should create search cursor with published timestamp."""
        article_id = uuid4()
        published_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        created_at = datetime(2024, 1, 2, 12, 0, 0, tzinfo=UTC)
        relevance = 0.95

        cursor_data = create_search_cursor_data(
            article_id, published_at, created_at, relevance
        )

        assert cursor_data["timestamp"] == "2024-01-01T12:00:00+00:00"
        assert cursor_data["is_published_at"] is True
        assert cursor_data["article_id"] == str(article_id)
        assert cursor_data["relevance"] == "0.95"

    async def test_create_search_cursor_without_published_at(self):
        """Should use created_at when published_at is None."""
        article_id = uuid4()
        published_at = None
        created_at = datetime(2024, 1, 2, 12, 0, 0, tzinfo=UTC)
        relevance = 0.85

        cursor_data = create_search_cursor_data(
            article_id, published_at, created_at, relevance
        )

        assert cursor_data["timestamp"] == "2024-01-02T12:00:00+00:00"
        assert cursor_data["is_published_at"] is False
        assert cursor_data["article_id"] == str(article_id)
        assert cursor_data["relevance"] == "0.85"

    async def test_create_search_cursor_with_zero_relevance(self):
        """Should handle zero relevance score."""
        article_id = uuid4()
        published_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        created_at = datetime(2024, 1, 2, 12, 0, 0, tzinfo=UTC)
        relevance = 0.0

        cursor_data = create_search_cursor_data(
            article_id, published_at, created_at, relevance
        )

        assert cursor_data["relevance"] == "0.0"


class TestCursorRoundTrip:
    """Test encode/decode round-trip."""

    async def test_article_cursor_round_trip(self):
        """Should encode and decode article cursor."""
        article_id = uuid4()
        published_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        created_at = datetime(2024, 1, 2, 12, 0, 0, tzinfo=UTC)

        original_data = create_article_cursor_data(
            article_id, published_at, created_at
        )
        encoded = encode_cursor_data(original_data)
        decoded = parse_cursor_data(encoded)

        assert decoded == original_data

    async def test_feed_cursor_round_trip(self):
        """Should encode and decode feed cursor."""
        feed_id = uuid4()
        last_update = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)

        original_data = create_feed_cursor_data(feed_id, last_update)
        encoded = encode_cursor_data(original_data)
        decoded = parse_cursor_data(encoded)

        assert decoded == original_data

    async def test_search_cursor_round_trip(self):
        """Should encode and decode search cursor."""
        article_id = uuid4()
        published_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        created_at = datetime(2024, 1, 2, 12, 0, 0, tzinfo=UTC)
        relevance = 0.92

        original_data = create_search_cursor_data(
            article_id, published_at, created_at, relevance
        )
        encoded = encode_cursor_data(original_data)
        decoded = parse_cursor_data(encoded)

        assert decoded == original_data
