from typing import Any


class ArticleDomain:
    @staticmethod
    def build_mark_all_message(request_data: Any) -> str:
        action = "read" if request_data.is_read else "unread"
        return f"Marked articles as {action}"

    @staticmethod
    def build_state_update_message(state_updated: bool) -> str:
        if state_updated:
            return "Article updated successfully"
        return "No changes made"
