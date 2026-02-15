"""Unit tests for entry content extraction."""

from datetime import UTC
from unittest.mock import MagicMock

from backend.infrastructure.feed.parsing.entry_content import EntryExtractor


class TestExtractContentFromEntry:
    """Test content extraction from entries."""

    def test_extracts_atom_content_from_list(self):
        """Should extract content from atom:content in list format."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.content = [{"value": "Article content"}]

        result = extractor.extract_content_from_entry(entry)

        assert result == ("Article content", "atom:content")

    def test_extracts_atom_content_from_string(self):
        """Should extract content from atom:content string."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.content = "Plain content"

        result = extractor.extract_content_from_entry(entry)

        assert result == ("Plain content", "atom:content")

    def test_extracts_content_encoded(self):
        """Should extract content from content:encoded tag."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.content = None
        entry.content_encoded = "Encoded content"

        result = extractor.extract_content_from_entry(entry)

        assert result == ("Encoded content", "content:encoded")

    def test_returns_none_when_no_content(self):
        """Should return None when no content found."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.content = None
        entry.content_encoded = None

        result = extractor.extract_content_from_entry(entry)

        assert result == (None, None)

    def test_skips_empty_content_in_list(self):
        """Should skip empty content items in list."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.content = [{"value": ""}, {"value": "Valid content"}]

        result = extractor.extract_content_from_entry(entry)

        assert result == ("Valid content", "atom:content")

    def test_skips_whitespace_only_content(self):
        """Should skip whitespace-only content."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.content = "   "

        result = extractor.extract_content_from_entry(entry)

        assert result == (None, None)


class TestExtractAuthorFromEntry:
    """Test author extraction from entries."""

    def test_extracts_author_name_from_dict(self):
        """Should extract author name from dict."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.author = {"name": "John Doe"}

        result = extractor.extract_author_from_entry(entry)

        assert result == "John Doe"

    def test_extracts_author_email_when_no_name(self):
        """Should extract email when no name present (no @)."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.author = {"email": "johndoe"}

        result = extractor.extract_author_from_entry(entry)

        assert result == "johndoe"

    def test_extracts_author_from_string(self):
        """Should extract author from string."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.author = "Jane Doe"

        result = extractor.extract_author_from_entry(entry)

        assert result == "Jane Doe"

    def test_extracts_first_author_from_list(self):
        """Should extract first author from list."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.author = [{"name": "Author One"}, {"name": "Author Two"}]

        result = extractor.extract_author_from_entry(entry)

        assert result == "Author One"

    def test_extracts_first_string_author_from_list(self):
        """Should extract first string author from list."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.author = ["Author One", "Author Two"]

        result = extractor.extract_author_from_entry(entry)

        assert result == "Author One"

    def test_extracts_dublin_core_creator(self):
        """Should extract from dc_creator field."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.author = None
        entry.dc_creator = "Creator Name"

        result = extractor.extract_author_from_entry(entry)

        assert result == "Creator Name"

    def test_joins_multiple_authors_from_list(self):
        """Should join multiple authors with comma."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.author = None
        entry.dc_creator = ["Author One", "Author Two", "Author Three"]

        result = extractor.extract_author_from_entry(entry)

        assert result == "Author One, Author Two, Author Three"

    def test_returns_none_when_no_author(self):
        """Should return None when no author found."""
        extractor = EntryExtractor()
        # Use a simple object without author attributes
        entry = type("Entry", (), {})()

        result = extractor.extract_author_from_entry(entry)

        assert result is None

    def test_fallback_to_string_for_author_dict_with_email_only(self):
        """Should fall back to string representation when author dict has only email."""
        extractor = EntryExtractor()
        # Use a simple object to avoid MagicMock wrapping the dict
        entry = type("Entry", (), {"author": {"email": "user@example.com"}})()

        result = extractor.extract_author_from_entry(entry)

        # When dict has only email with @ and no name, falls back to str(dict)
        assert result == "{'email': 'user@example.com'}"


class TestExtractCategoriesFromEntry:
    """Test category extraction from entries."""

    def test_extracts_tags_from_term_dict(self):
        """Should extract categories from tag term dict."""
        extractor = EntryExtractor()
        entry = type(
            "Entry",
            (),
            {
                "tags": [{"term": "tech"}, {"term": "news"}],
            },
        )()

        result = extractor.extract_categories_from_entry(entry)

        assert result == ["tech", "news"]

    def test_extracts_tags_from_string_list(self):
        """Should extract categories from string tag list."""
        extractor = EntryExtractor()
        entry = type(
            "Entry",
            (),
            {
                "tags": ["tag1", "tag2"],
            },
        )()

        result = extractor.extract_categories_from_entry(entry)

        assert result == ["tag1", "tag2"]

    def test_extracts_category_from_list(self):
        """Should extract categories from category list."""
        extractor = EntryExtractor()
        entry = type(
            "Entry", (), {"tags": None, "category": ["cat1", "cat2"]}
        )()

        result = extractor.extract_categories_from_entry(entry)

        assert result == ["cat1", "cat2"]

    def test_extracts_category_from_string(self):
        """Should extract category from string."""
        extractor = EntryExtractor()
        entry = type("Entry", (), {"tags": None, "category": "single-cat"})()

        result = extractor.extract_categories_from_entry(entry)

        assert result == ["single-cat"]

    def test_extracts_subject_from_list(self):
        """Should extract from subject list."""
        extractor = EntryExtractor()
        entry = type(
            "Entry",
            (),
            {"tags": None, "category": None, "subject": ["subj1", "subj2"]},
        )()

        result = extractor.extract_categories_from_entry(entry)

        assert result == ["subj1", "subj2"]

    def test_extracts_dc_subject_field(self):
        """Should extract from dc_subject field."""
        extractor = EntryExtractor()
        entry = type(
            "Entry",
            (),
            {
                "tags": None,
                "category": None,
                "subject": None,
                "dc_subject": "dc-tag",
            },
        )()

        result = extractor.extract_categories_from_entry(entry)

        assert result == ["dc-tag"]

    def test_deduplicates_categories(self):
        """Should deduplicate categories while preserving order."""
        extractor = EntryExtractor()
        entry = type(
            "Entry",
            (),
            {
                "tags": [{"term": "tech"}, {"term": "news"}],
                "category": "tech",
                "subject": ["news"],
            },
        )()

        result = extractor.extract_categories_from_entry(entry)

        assert result == ["tech", "news"]
        assert len(result) == len(set(result))  # All unique

    def test_returns_empty_list_when_no_categories(self):
        """Should return empty list when no categories found."""
        extractor = EntryExtractor()
        entry = type("Entry", (), {"tags": None, "category": None})()

        result = extractor.extract_categories_from_entry(entry)

        assert result == []


class TestExtractPublishDate:
    """Test publish date extraction from entries."""

    def test_extracts_published_parsed_date(self):
        """Should extract date from published_parsed field."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.published_parsed = (
            2024,
            1,
            15,
            10,
            30,
            0,
            0,
            0,
            0,
        )  # time.struct_time

        result = extractor.extract_publish_date(entry)

        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_extracts_updated_parsed_date(self):
        """Should extract date from updated_parsed field."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.published_parsed = None
        entry.updated_parsed = (2024, 2, 20, 12, 0, 0, 0, 0, 0)

        result = extractor.extract_publish_date(entry)

        assert result is not None
        assert result.year == 2024
        assert result.month == 2

    def test_extracts_published_string_date(self):
        """Should extract and parse published string date."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.published_parsed = None
        entry.updated_parsed = None
        entry.published = "2024-01-15T10:30:00Z"

        result = extractor.extract_publish_date(entry)

        assert result is not None
        assert result.year == 2024

    def test_extracts_created_string_date(self):
        """Should extract and parse created string date."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.published_parsed = None
        entry.updated_parsed = None
        entry.published = None
        entry.updated = None
        entry.created = "2024-03-01T12:00:00Z"

        result = extractor.extract_publish_date(entry)

        assert result is not None
        assert result.month == 3

    def test_extracts_pub_date_field(self):
        """Should extract from pubDate RSS field."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.published_parsed = None
        entry.updated_parsed = None
        entry.published = None
        entry.updated = None
        entry.created = None
        entry.date = "2024-04-01 14:00:00Z"

        result = extractor.extract_publish_date(entry)

        assert result is not None
        assert result.month == 4

    def test_returns_none_when_no_date_found(self):
        """Should return None when no date fields found."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.published_parsed = None
        entry.updated_parsed = None
        entry.published = None
        entry.updated = None
        entry.created = None
        entry.date = None
        entry.pubDate = None

        result = extractor.extract_publish_date(entry)

        assert result is None

    def test_returns_utc_timezone(self):
        """Should return dates in UTC timezone."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.published_parsed = (2024, 1, 15, 10, 30, 0, 0, 0, 0)

        result = extractor.extract_publish_date(entry)

        assert result is not None
        assert result.tzinfo == UTC

    def test_handles_invalid_time_struct(self):
        """Should handle invalid time struct gracefully."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.published_parsed = (2024, 1, 15)  # Too short

        extractor.extract_publish_date(entry)

        # Should fall back to other fields or return None
        # For this test, we'll check it doesn't crash
        assert True  # Test passes if no exception

    def test_handles_future_dates(self):
        """Should handle future dates normally."""
        extractor = EntryExtractor()
        entry = MagicMock()
        entry.published_parsed = (2099, 12, 31, 23, 59, 59, 0, 0, 0)

        result = extractor.extract_publish_date(entry)

        assert result is not None
        assert result.year == 2099
