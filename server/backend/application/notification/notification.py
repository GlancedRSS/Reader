"""Orchestrates SSE notification streams for real-time updates."""

from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any
from uuid import UUID

from backend.infrastructure.notifications.notifications import event_stream


class NotificationApplication:
    """Application service for managing SSE notification streams."""

    async def get_notification_stream(
        self,
        user_id: UUID,
        is_disconnect: Callable[[], Awaitable[bool]] | None = None,
    ) -> AsyncGenerator[dict[str, Any]]:
        """Get the SSE event stream for a user's notifications.

        Args:
            user_id: The user to stream notifications for.
            is_disconnect: Callable that returns an awaitable bool for disconnect status.

        Yields:
            SSE event dictionaries with 'event' and 'data' keys.

        """
        if is_disconnect is None:

            async def never_disconnect() -> bool:
                return False

            is_disconnect = never_disconnect

        async for event in event_stream(user_id, is_disconnect):
            yield event
