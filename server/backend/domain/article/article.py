"""Message building for articles."""

from typing import Any


class ArticleDomain:
    """Message building for articles."""

    @staticmethod
    def build_mark_all_message(request_data: Any) -> str:
        """Build appropriate message for mark-all operations.

        Args:
            request_data: Request object with is_read attribute

        Returns:
            User-friendly message describing the operation

        """
        action = "read" if request_data.is_read else "unread"
        return f"Marked articles as {action}"

    @staticmethod
    def build_state_update_message(state_updated: bool) -> str:
        """Build appropriate message for state update operations.

        Args:
            state_updated: Whether the state was actually changed

        Returns:
            User-friendly message describing the result

        """
        if state_updated:
            return "Article updated successfully"
        return "No changes made"
