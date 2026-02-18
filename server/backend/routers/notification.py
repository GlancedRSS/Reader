"""Server-Sent Events (SSE) endpoint for real-time notifications."""

import json
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse

from backend.core.dependencies import get_notification_application

router = APIRouter()


async def _error_stream(message: str) -> AsyncGenerator[dict[str, Any]]:
    """Yield a single error event and close."""
    yield {"event": "error", "data": json.dumps({"message": message})}


@router.get(
    "",
    summary="Server-Sent Events stream",
    description="Connect to receive real-time notifications. Keep the connection open for continuous updates.",
    tags=["Notifications"],
)
async def notifications_stream(
    request: Request,
    notification_app=Depends(get_notification_application),
) -> EventSourceResponse:
    """SSE endpoint for real-time notifications."""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        return EventSourceResponse(
            _error_stream("Authentication required"),
            media_type="text/event-stream",
        )

    async def event_generator() -> AsyncGenerator[dict[str, Any]]:
        try:
            async for event in notification_app.get_notification_stream(
                user_id, request.is_disconnected
            ):
                yield event
        except Exception as e:
            yield {"event": "error", "data": f"Stream error: {e!s}"}

    return EventSourceResponse(
        event_generator(),
        media_type="text/event-stream",
        ping=15,
    )
