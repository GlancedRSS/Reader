"""Unit tests for ArticleDomain."""

from unittest.mock import MagicMock

from backend.domain.article.article import ArticleDomain


class TestBuildMarkAllMessage:
    """Test build_mark_all_message method."""

    def test_mark_as_read_message(self):
        """Should return 'read' message when is_read is True."""
        request_data = MagicMock(is_read=True)
        result = ArticleDomain.build_mark_all_message(request_data)
        assert result == "Marked articles as read"

    def test_mark_as_unread_message(self):
        """Should return 'unread' message when is_read is False."""
        request_data = MagicMock(is_read=False)
        result = ArticleDomain.build_mark_all_message(request_data)
        assert result == "Marked articles as unread"


class TestBuildStateUpdateMessage:
    """Test build_state_update_message method."""

    def test_state_updated_message(self):
        """Should return success message when state was updated."""
        result = ArticleDomain.build_state_update_message(state_updated=True)
        assert result == "Article updated successfully"

    def test_state_not_updated_message(self):
        """Should return no changes message when state was not updated."""
        result = ArticleDomain.build_state_update_message(state_updated=False)
        assert result == "No changes made"
