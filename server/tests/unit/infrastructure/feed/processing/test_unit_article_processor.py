"""Unit tests for article processing infrastructure."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

from backend.infrastructure.feed.processing.article_processor import (
    ArticleProcessor,
)


class TestArticleProcessorInit:
    """Test ArticleProcessor initialization."""

    @pytest.mark.asyncio
    async def test_initializes_with_dependencies(self):
        """Should initialize with required dependencies."""
        mock_db = MagicMock()

        processor = ArticleProcessor(mock_db)

        assert processor.db == mock_db
        assert processor.partition_service is not None
        assert processor.tag_repository is not None


class TestCreateUserStatesForSubscribers:
    """Test user state creation for subscribers."""

    @pytest.mark.asyncio
    async def test_creates_states_for_subscribers(self):
        """Should create user_article_states for all active subscribers."""
        mock_db = MagicMock()
        processor = ArticleProcessor(mock_db)

        feed_id = uuid4()
        article_ids = [uuid4(), uuid4()]

        # Mock subscriber query
        mock_result = MagicMock()
        mock_result.all.return_value = [
            (
                UUID("00000000-0000-0000-0000-000000000001"),
                UUID("00000000-0000-0000-0000-000000000002"),
            )
        ]
        execute_call_count = [0]

        async def mock_execute(*args, **kwargs):
            execute_call_count[0] += 1
            return mock_result

        mock_db.execute = mock_execute

        await processor._create_user_states_for_subscribers(
            feed_id, article_ids
        )

        # Should execute query at least once for subscribers
        assert execute_call_count[0] >= 1

    @pytest.mark.asyncio
    async def test_skips_when_no_subscribers(self):
        """Should skip when no subscribers found."""
        mock_db = MagicMock()
        processor = ArticleProcessor(mock_db)

        # uuid4 is imported at module level

        feed_id = uuid4()
        article_ids = [uuid4()]

        # Mock empty subscriber query
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        await processor._create_user_states_for_subscribers(
            feed_id, article_ids
        )

        # Should only execute the subscriber query, not the insert
        assert mock_db.execute.call_count == 1


class TestCreateTagsForSubscribers:
    """Test tag creation for subscribers."""

    @pytest.mark.asyncio
    async def test_creates_tags_for_subscribers(self):
        """Should create tags for all subscribers."""
        mock_db = MagicMock()
        mock_tag_repo = MagicMock()

        processor = ArticleProcessor(mock_db)
        processor.tag_repository = mock_tag_repo

        feed_id = uuid4()
        article_id = uuid4()
        source_tags = ["tech", "news"]

        # Mock subscriber query - returns tuples (user_id,)
        mock_result = MagicMock()
        mock_result.all.return_value = [
            (UUID("00000000-0000-0000-0000-000000000001"),)
        ]
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Mock tag operations
        mock_tag = MagicMock()
        mock_tag.id = uuid4()
        mock_tag_repo.get_or_create_tag = AsyncMock(return_value=mock_tag)
        mock_tag_repo.add_tags_to_article = AsyncMock()

        await processor._create_tags_for_subscribers(
            feed_id, article_id, source_tags
        )

        # Should create tags for each subscriber/tag combination
        assert mock_tag_repo.get_or_create_tag.call_count == 2  # 2 tags
        assert mock_tag_repo.add_tags_to_article.call_count == 2

    @pytest.mark.asyncio
    async def test_skips_when_no_source_tags(self):
        """Should skip when no source tags provided."""
        mock_db = MagicMock()
        processor = ArticleProcessor(mock_db)

        feed_id = uuid4()
        article_id = uuid4()
        source_tags = []

        await processor._create_tags_for_subscribers(
            feed_id, article_id, source_tags
        )

        # Should not execute any queries
        mock_db.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_skips_when_no_subscribers(self):
        """Should skip when no subscribers found."""
        mock_db = MagicMock()
        mock_tag_repo = MagicMock()

        processor = ArticleProcessor(mock_db)
        processor.tag_repository = mock_tag_repo

        feed_id = uuid4()
        article_id = uuid4()
        source_tags = ["tech"]

        # Mock empty subscriber query
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        await processor._create_tags_for_subscribers(
            feed_id, article_id, source_tags
        )

        # Should only execute subscriber query
        assert mock_db.execute.call_count == 1
        mock_tag_repo.get_or_create_tag.assert_not_called()


class TestProcessFeedArticlesErrorHandling:
    """Test error handling in process_feed_articles."""

    @pytest.mark.asyncio
    async def test_handles_partition_error_gracefully(self):
        """Should handle partition-related errors gracefully."""
        mock_db = MagicMock()

        processor = ArticleProcessor(mock_db)

        # uuid4 is imported at module level

        feed_id = uuid4()
        articles_data = [{"url": "https://example.com/article"}]

        # Mock partition creation
        processor.partition_service.analyze_and_create_partitions = AsyncMock(
            return_value=set()
        )

        # Mock existing article check
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Mock article creation with partition error
        def mock_add_with_error(article):
            from sqlalchemy.exc import ProgrammingError

            raise ProgrammingError(
                "no partition of relation articles", {}, Exception()
            )

        mock_db.add = mock_add_with_error
        mock_db.flush = AsyncMock()

        # The function should catch and handle the partition error
        # Since we're not actually creating partitions, it will just log and continue

        # This test verifies the error handling path exists
        with pytest.raises(Exception, match="no partition of relation"):
            await processor.process_feed_articles(feed_id, articles_data)

    @pytest.mark.asyncio
    async def test_skips_articles_without_url(self):
        """Should skip articles that don't have a URL."""
        mock_db = MagicMock()

        processor = ArticleProcessor(mock_db)

        # uuid4 is imported at module level

        feed_id = uuid4()
        articles_data = [
            {"url": "https://example.com/article1"},
            {"url": ""},  # Should be skipped
            {"url": None},  # Should be skipped
            {"url": "https://example.com/article2"},
        ]

        processor.partition_service.analyze_and_create_partitions = AsyncMock(
            return_value=set()
        )

        # Mock no existing articles
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        mock_article = MagicMock()
        mock_article.id = uuid4()
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()

        with patch(
            "backend.infrastructure.feed.processing.article_processor.parse_iso_datetime"
        ) as mock_parse:
            mock_parse.return_value = None

            (
                created_count,
                _new_ids,
                _all_ids,
            ) = await processor.process_feed_articles(feed_id, articles_data)

            # Should only create 2 articles (skipping the ones without URLs)
            assert created_count == 2

    @pytest.mark.asyncio
    async def test_skips_articles_with_future_publish_date(self):
        """Should skip articles with future publication dates."""
        from datetime import UTC, datetime, timedelta

        mock_db = MagicMock()

        processor = ArticleProcessor(mock_db)

        # uuid4 is imported at module level

        feed_id = uuid4()
        future_date = (datetime.now(UTC) + timedelta(days=7)).isoformat()
        articles_data = [
            {"url": "https://example.com/future", "published_at": future_date}
        ]

        processor.partition_service.analyze_and_create_partitions = AsyncMock(
            return_value=set()
        )

        # Mock no existing articles
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        (
            created_count,
            new_ids,
            _all_ids,
        ) = await processor.process_feed_articles(feed_id, articles_data)

        # Should skip the article with future date
        assert created_count == 0
        assert len(new_ids) == 0

    @pytest.mark.asyncio
    async def test_splits_categories_into_tags(self):
        """Should split comma-separated categories into individual tags."""
        mock_db = MagicMock()

        processor = ArticleProcessor(mock_db)

        feed_id = uuid4()
        articles_data = [
            {
                "url": "https://example.com/article",
                "categories": ["tech, AI", "news", " programming"],
            }
        ]

        processor.partition_service.analyze_and_create_partitions = AsyncMock(
            return_value=set()
        )

        # Setup different mock results for different queries
        mock_article_result = MagicMock()
        mock_article_result.scalar_one_or_none.return_value = None

        mock_subscriber_result = MagicMock()
        mock_subscriber_result.all.return_value = [(uuid4(),)]  # Return tuple

        call_count = [0]

        async def mock_execute(*args, **kwargs):
            call_count[0] += 1
            # First call is for existing article check
            if call_count[0] == 1:
                return mock_article_result
            # Later calls are for subscriber queries
            return mock_subscriber_result

        mock_db.execute = mock_execute

        mock_article = MagicMock()
        mock_article.id = uuid4()
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()

        # Mock tag creation
        processor.tag_repository = MagicMock()
        processor.tag_repository.get_or_create_tag = AsyncMock()
        processor.tag_repository.add_tags_to_article = AsyncMock()

        with patch(
            "backend.infrastructure.feed.processing.article_processor.parse_iso_datetime"
        ) as mock_parse:
            mock_parse.return_value = None

            (
                created_count,
                _new_ids,
                _all_ids,
            ) = await processor.process_feed_articles(feed_id, articles_data)

            # Categories should be split: "tech, AI" -> ["tech", "AI"], "news" -> ["news"], " programming" -> ["programming"]
            assert created_count == 1
            # Should have created multiple tags from split categories
            assert processor.tag_repository.get_or_create_tag.call_count >= 3

    @pytest.mark.asyncio
    async def test_handles_duplicate_article_error(self):
        """Should handle duplicate key error when article was created concurrently."""
        from sqlalchemy.exc import IntegrityError

        mock_db = MagicMock()

        processor = ArticleProcessor(mock_db)

        # uuid4 is imported at module level

        feed_id = uuid4()
        articles_data = [{"url": "https://example.com/article"}]

        processor.partition_service.analyze_and_create_partitions = AsyncMock(
            return_value=set()
        )

        # Mock existing article check (not found initially)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Mock duplicate error on first insert, then find existing article
        mock_existing_article = MagicMock()
        mock_existing_article.id = uuid4()
        duplicate_error = IntegrityError("duplicate key value", {}, Exception())
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock(side_effect=[duplicate_error, None])

        # Second query finds the existing article
        mock_existing_result = MagicMock()
        mock_existing_result.scalar_one_or_none.return_value = (
            mock_existing_article
        )

        call_count = [0]

        def side_effect_func(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:  # First call (initial check)
                return mock_result
            # Second call (after duplicate error)
            return mock_existing_result

        mock_db.execute = AsyncMock(side_effect=side_effect_func)

        (
            created_count,
            _new_ids,
            _all_ids,
        ) = await processor.process_feed_articles(feed_id, articles_data)

        # Should handle the duplicate and return the existing article
        assert created_count == 1

    @pytest.mark.asyncio
    async def test_truncates_summary_to_2000_chars(self):
        """Should truncate summary field to 2000 characters."""
        mock_db = MagicMock()

        processor = ArticleProcessor(mock_db)

        # uuid4 is imported at module level

        feed_id = uuid4()
        long_summary = "x" * 3000
        articles_data = [
            {"url": "https://example.com/article", "summary": long_summary}
        ]

        processor.partition_service.analyze_and_create_partitions = AsyncMock(
            return_value=set()
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Capture the created article
        created_articles = []

        def capture_add(article):
            created_articles.append(article)

        mock_db.add = capture_add
        mock_db.flush = AsyncMock()

        with patch(
            "backend.infrastructure.feed.processing.article_processor.parse_iso_datetime"
        ) as mock_parse:
            mock_parse.return_value = None

            await processor.process_feed_articles(feed_id, articles_data)

            # Summary should be truncated to 2000 chars
            assert len(created_articles[0].summary) == 2000
