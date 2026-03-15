from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any
from uuid import UUID

from backend.infrastructure.notifications.notifications import event_stream


class NotificationApplication:
    async def get_notification_stream(
        self,
        user_id: UUID,
        is_disconnect: Callable[[], Awaitable[bool]] | None = None,
    ) -> AsyncGenerator[dict[str, Any]]:
        if is_disconnect is None:

            async def never_disconnect() -> bool:
                return False

            is_disconnect = never_disconnect

        async for event in event_stream(user_id, is_disconnect):
            yield event
