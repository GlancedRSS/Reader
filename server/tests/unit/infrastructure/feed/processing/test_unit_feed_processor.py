"""Unit tests for feed processing infrastructure."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.infrastructure.feed.processing.feed_processor import FeedProcessor


class TestExtractFeedContent:
    """Test feed content extraction."""

    @pytest.mark.asyncio
    async def test_extracts_content_from_entry(self):
        """Should extract content and metadata from RSS entry."""
        processor = FeedProcessor(MagicMock())

        entry = MagicMock()
        entry.get = MagicMock(return_value="")

        processor.entry_extractor.extract_content_from_entry = MagicMock(
            return_value=("<p>Content</p>", "summary")
        )
        processor.media_extractor.extract_image_from_entry = MagicMock(
            return_value=None
        )
        processor.media_extractor.extract_image_from_summary_description = (
            MagicMock(return_value=None)
        )
        processor.entry_extractor.extract_author_from_entry = MagicMock(
            return_value="Author"
        )
        processor.entry_extractor.extract_categories_from_entry = MagicMock(
            return_value=["tag1", "tag2"]
        )
        processor.media_extractor.extract_metadata_from_entry = MagicMock(
            return_value={}
        )
        processor.html_cleaner.clean_html = MagicMock(return_value="clean")
        processor.html_cleaner.html_to_text = MagicMock(return_value="text")

        result = processor.extract_feed_content(entry)

        assert result == (
            "clean",
            "text",
            None,
            "Author",
            ["tag1", "tag2"],
            "summary",
            {},  # platform_metadata
        )

    @pytest.mark.asyncio
    async def test_extracts_image_from_entry(self):
        """Should extract image URL from entry media."""
        processor = FeedProcessor(MagicMock())

        entry = MagicMock()
        entry.get = MagicMock(return_value="")

        processor.entry_extractor.extract_content_from_entry = MagicMock(
            return_value=("<p>Content</p>", "summary")
        )
        processor.media_extractor.extract_image_from_entry = MagicMock(
            return_value="https://example.com/image.jpg"
        )
        processor.entry_extractor.extract_author_from_entry = MagicMock(
            return_value=None
        )
        processor.entry_extractor.extract_categories_from_entry = MagicMock(
            return_value=[]
        )
        processor.html_cleaner.clean_html = MagicMock(return_value="")
        processor.html_cleaner.html_to_text = MagicMock(return_value="")

        result = processor.extract_feed_content(entry)

        assert result[2] == "https://example.com/image.jpg"

    @pytest.mark.asyncio
    async def test_extracts_image_from_summary_when_no_entry_image(self):
        """Should extract image from summary when no entry image."""
        processor = FeedProcessor(MagicMock())

        entry = MagicMock()
        entry.get = MagicMock(return_value="")

        processor.entry_extractor.extract_content_from_entry = MagicMock(
            return_value=("<p>Content</p>", "summary")
        )
        processor.media_extractor.extract_image_from_entry = MagicMock(
            return_value=None
        )
        processor.media_extractor.extract_image_from_summary_description = (
            MagicMock(return_value="https://example.com/image.jpg")
        )
        processor.entry_extractor.extract_author_from_entry = MagicMock(
            return_value=None
        )
        processor.entry_extractor.extract_categories_from_entry = MagicMock(
            return_value=[]
        )
        processor.media_extractor.extract_metadata_from_entry = MagicMock(
            return_value={}
        )
        processor.html_cleaner.clean_html = MagicMock(return_value="")
        processor.html_cleaner.html_to_text = MagicMock(return_value="")

        result = processor.extract_feed_content(entry)

        assert result[2] == "https://example.com/image.jpg"

    @pytest.mark.asyncio
    async def test_extracts_image_from_html_content_when_no_other_images(self):
        """Should extract image from HTML content when no other images found."""
        processor = FeedProcessor(MagicMock())

        entry = MagicMock()
        entry.get = MagicMock(return_value="")

        processor.entry_extractor.extract_content_from_entry = MagicMock(
            return_value=(
                '<img src="https://example.com/image.jpg">',
                "summary",
            )
        )
        processor.media_extractor.extract_image_from_entry = MagicMock(
            return_value=None
        )
        processor.media_extractor.extract_image_from_summary_description = (
            MagicMock(return_value=None)
        )
        processor.media_extractor.extract_image_from_html = MagicMock(
            return_value="https://example.com/image.jpg"
        )
        processor.entry_extractor.extract_author_from_entry = MagicMock(
            return_value=None
        )
        processor.entry_extractor.extract_categories_from_entry = MagicMock(
            return_value=[]
        )
        processor.html_cleaner.clean_html = MagicMock(return_value="")
        processor.html_cleaner.html_to_text = MagicMock(return_value="")

        result = processor.extract_feed_content(entry)

        assert result[2] == "https://example.com/image.jpg"

    @pytest.mark.asyncio
    async def test_returns_empty_strings_when_no_content(self):
        """Should return empty content strings when entry has no content."""
        processor = FeedProcessor(MagicMock())

        entry = MagicMock()
        entry.get = MagicMock(return_value=None)

        processor.entry_extractor.extract_content_from_entry = MagicMock(
            return_value=(None, None)
        )
        processor.media_extractor.extract_image_from_entry = MagicMock(
            return_value=None
        )
        processor.media_extractor.extract_image_from_summary_description = (
            MagicMock(return_value=None)
        )
        processor.entry_extractor.extract_author_from_entry = MagicMock(
            return_value=None
        )
        processor.entry_extractor.extract_categories_from_entry = MagicMock(
            return_value=[]
        )
        processor.media_extractor.extract_metadata_from_entry = MagicMock(
            return_value={}
        )

        result = processor.extract_feed_content(entry)

        assert result == ("", "", None, None, [], None, {})


class TestParseFeedEntries:
    """Test feed entry parsing."""

    @pytest.mark.asyncio
    async def test_parses_single_entry(self):
        """Should parse a single feed entry."""
        processor = FeedProcessor(MagicMock())

        feed = MagicMock()
        entry = MagicMock()
        entry.get = MagicMock(return_value="Test Entry")
        feed.entries = [entry]

        processor.extract_feed_content = MagicMock(
            return_value=(
                "<p>Content</p>",
                "search",
                "https://example.com/img.jpg",
                "Author",
                ["tag"],
                "html",
                {},  # platform_metadata
            )
        )
        processor.html_cleaner.html_to_text = MagicMock(
            return_value="summary text"
        )

        result = processor._parse_feed_entries(feed)

        assert len(result) == 1
        assert result[0]["title"] == "Test Entry"

    @pytest.mark.asyncio
    async def test_limits_to_max_50_entries(self):
        """Should only process up to 50 entries."""
        processor = FeedProcessor(MagicMock())

        feed = MagicMock()
        feed.entries = [MagicMock() for _ in range(100)]
        for entry in feed.entries:
            entry.get = MagicMock(return_value="Entry")

        processor.extract_feed_content = MagicMock(
            return_value=("", "", None, None, [], "html", {})
        )
        processor.html_cleaner.html_to_text = MagicMock(return_value="summary")

        result = processor._parse_feed_entries(feed)

        assert len(result) == 50

    @pytest.mark.asyncio
    async def test_returns_empty_list_for_no_entries(self):
        """Should return empty list when feed has no entries."""
        processor = FeedProcessor(MagicMock())

        feed = MagicMock()
        feed.entries = []

        result = processor._parse_feed_entries(feed)

        assert result == []

    @pytest.mark.asyncio
    async def test_decodes_html_entities_in_title(self):
        """Should decode HTML entities in entry title."""
        processor = FeedProcessor(MagicMock())

        feed = MagicMock()
        entry = MagicMock()
        entry.get = MagicMock(
            side_effect=lambda k, d=None: {
                "title": "Test &amp; Article",
                "link": "https://example.com/article",
                "summary": None,
                "description": None,
            }.get(k, d)
        )
        feed.entries = [entry]

        processor.extract_feed_content = MagicMock(
            return_value=("", "", None, None, [], "html", {})
        )
        processor.html_cleaner.html_to_text = MagicMock(return_value="")

        result = processor._parse_feed_entries(feed)

        assert result[0]["title"] == "Test & Article"


class TestGetFeedById:
    """Test get_feed_by_id method."""

    @pytest.mark.asyncio
    async def test_delegates_to_repository(self):
        """Should delegate to repository."""
        mock_repo = MagicMock()
        mock_repo.get_feed_by_id = AsyncMock(return_value="feed")

        processor = FeedProcessor(MagicMock())
        processor.repository = mock_repo

        from uuid import UUID

        result = await processor.get_feed_by_id(
            UUID("00000000-0000-0000-0000-000000000001")
        )

        mock_repo.get_feed_by_id.assert_called_once()
        assert result == "feed"


class TestDeleteFeed:
    """Test feed deletion."""

    @pytest.mark.asyncio
    async def test_deletes_existing_feed(self):
        """Should delete existing feed."""
        mock_repo = MagicMock()
        mock_repo.get_feed_by_id = AsyncMock(return_value=MagicMock())
        mock_repo.delete_feed = AsyncMock()

        processor = FeedProcessor(MagicMock())
        processor.repository = mock_repo

        from uuid import UUID

        result = await processor.delete_feed(
            UUID("00000000-0000-0000-0000-000000000001")
        )

        assert result is True
        mock_repo.delete_feed.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_false_for_nonexistent_feed(self):
        """Should return False for non-existent feed."""
        mock_repo = MagicMock()
        mock_repo.get_feed_by_id = AsyncMock(return_value=None)

        processor = FeedProcessor(MagicMock())
        processor.repository = mock_repo

        from uuid import UUID

        result = await processor.delete_feed(
            UUID("00000000-0000-0000-0000-000000000001")
        )

        assert result is False


class TestUpdateFeed:
    """Test feed update."""

    @pytest.mark.asyncio
    async def test_updates_feed_title(self):
        """Should update feed title."""
        mock_repo = MagicMock()
        mock_feed = MagicMock()
        mock_repo.get_feed_by_id = AsyncMock(return_value=mock_feed)
        mock_repo.update_feed = AsyncMock(return_value=mock_feed)

        processor = FeedProcessor(MagicMock())
        processor.repository = mock_repo

        from uuid import UUID

        from backend.schemas.feeds import FeedUpdateRequest

        request = FeedUpdateRequest(title="New Title")

        await processor.update_feed(
            UUID("00000000-0000-0000-0000-000000000001"), request
        )

        mock_repo.update_feed.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_none_for_nonexistent_feed(self):
        """Should return None when feed not found."""
        mock_repo = MagicMock()
        mock_repo.get_feed_by_id = AsyncMock(return_value=None)

        processor = FeedProcessor(MagicMock())
        processor.repository = mock_repo

        from uuid import UUID

        from backend.schemas.feeds import FeedUpdateRequest

        request = FeedUpdateRequest(title="New Title")

        result = await processor.update_feed(
            UUID("00000000-0000-0000-0000-000000000001"), request
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_updates_description(self):
        """Should update feed description."""
        mock_repo = MagicMock()
        mock_feed = MagicMock()
        mock_repo.get_feed_by_id = AsyncMock(return_value=mock_feed)
        mock_repo.update_feed = AsyncMock(return_value=mock_feed)

        processor = FeedProcessor(MagicMock())
        processor.repository = mock_repo

        from uuid import UUID

        from backend.schemas.feeds import FeedUpdateRequest

        request = FeedUpdateRequest(description="New description")

        await processor.update_feed(
            UUID("00000000-0000-0000-0000-000000000001"), request
        )

        # Verify update was called with description
        call_args = mock_repo.update_feed.call_args
        assert call_args[0][1]["description"] == "New description"
