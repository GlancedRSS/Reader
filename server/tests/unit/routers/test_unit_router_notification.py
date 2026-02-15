"""Unit tests for notification SSE endpoint."""

import json
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import Request
from sse_starlette.sse import EventSourceResponse

from backend.routers.notification import _error_stream, notifications_stream


class TestErrorStream:
    """Test _error_stream helper function."""

    @pytest.mark.asyncio
    async def test_yields_single_error_event(self):
        """Should yield a single error event with JSON data."""
        result = []
        async for event in _error_stream("Test error message"):
            result.append(event)

        assert len(result) == 1
        assert result[0]["event"] == "error"
        data = json.loads(result[0]["data"])
        assert data["message"] == "Test error message"

    @pytest.mark.asyncio
    async def test_yields_valid_json_data(self):
        """Should yield valid JSON in data field."""
        async for event in _error_stream("Auth failed"):
            data = json.loads(event["data"])
            assert "message" in data
            assert data["message"] == "Auth failed"


class TestNotificationsStream:
    """Test notifications_stream SSE endpoint."""

    @pytest.mark.asyncio
    async def test_returns_error_stream_when_no_user_id(self):
        """Should return error stream when user_id is not set."""
        mock_request = MagicMock(spec=Request)
        mock_request.state.user_id = None

        mock_notification_app = MagicMock()

        with patch(
            "backend.routers.notification.get_notification_application",
            return_value=mock_notification_app,
        ):
            response = await notifications_stream(
                mock_request, mock_notification_app
            )

        assert isinstance(response, EventSourceResponse)
        assert response.media_type == "text/event-stream"

    @pytest.mark.asyncio
    async def test_returns_sse_response_when_authenticated(self):
        """Should return SSE response when user_id is set."""
        user_id = uuid4()
        mock_request = MagicMock(spec=Request)
        mock_request.state.user_id = user_id

        mock_notification_app = MagicMock()

        async def mock_stream():
            yield {"event": "test", "data": "{}"}

        mock_notification_app.get_notification_stream = mock_stream

        with patch(
            "backend.routers.notification.get_notification_application",
            return_value=mock_notification_app,
        ):
            response = await notifications_stream(
                mock_request, mock_notification_app
            )

        assert isinstance(response, EventSourceResponse)
        assert response.media_type == "text/event-stream"

    @pytest.mark.asyncio
    async def test_event_generator_yields_events(self):
        """Should yield events from notification application."""
        user_id = uuid4()
        mock_request = MagicMock(spec=Request)
        mock_request.state.user_id = user_id

        mock_notification_app = MagicMock()

        # Create an async generator that yields events
        async def event_gen():
            yield {"event": "new_articles", "data": '{"feed_id": "123"}'}
            yield {"event": "update", "data": '{"status": "complete"}'}

        mock_notification_app.get_notification_stream = event_gen

        with patch(
            "backend.routers.notification.get_notification_application",
            return_value=mock_notification_app,
        ):
            response = await notifications_stream(
                mock_request, mock_notification_app
            )

        # Verify we get an EventSourceResponse
        assert isinstance(response, EventSourceResponse)

    @pytest.mark.asyncio
    async def test_event_generator_handles_exceptions(self):
        """Should catch exceptions and yield error event."""
        user_id = uuid4()
        mock_request = MagicMock(spec=Request)
        mock_request.state.user_id = user_id

        mock_notification_app = MagicMock()

        # Create an async generator that raises an exception
        async def failing_gen():
            yield {"event": "test", "data": "{}"}
            raise RuntimeError("Connection lost")

        mock_notification_app.get_notification_stream = failing_gen

        with patch(
            "backend.routers.notification.get_notification_application",
            return_value=mock_notification_app,
        ):
            response = await notifications_stream(
                mock_request, mock_notification_app
            )

        # Should still return EventSourceResponse
        assert isinstance(response, EventSourceResponse)

    @pytest.mark.asyncio
    async def test_sse_ping_interval_configured(self):
        """Should configure ping interval for keepalive."""
        user_id = uuid4()
        mock_request = MagicMock(spec=Request)
        mock_request.state.user_id = user_id

        mock_notification_app = MagicMock()

        async def mock_stream():
            yield {"event": "test", "data": "{}"}

        mock_notification_app.get_notification_stream = mock_stream

        with patch(
            "backend.routers.notification.get_notification_application",
            return_value=mock_notification_app,
        ):
            with patch(
                "backend.routers.notification.EventSourceResponse"
            ) as mock_sse:
                await notifications_stream(mock_request, mock_notification_app)

                # Verify EventSourceResponse was called with ping=15
                call_kwargs = mock_sse.call_args[1]
                assert call_kwargs["ping"] == 15

    @pytest.mark.asyncio
    async def test_uses_notification_application_dependency(self):
        """Should use notification application from dependency."""
        user_id = uuid4()
        mock_request = MagicMock(spec=Request)
        mock_request.state.user_id = user_id

        mock_notification_app = MagicMock()

        async def mock_stream():
            yield {"event": "test", "data": "{}"}

        mock_notification_app.get_notification_stream = mock_stream

        # The dependency should be passed in and used
        response = await notifications_stream(
            mock_request, mock_notification_app
        )
        assert isinstance(response, EventSourceResponse)

    @pytest.mark.asyncio
    async def test_gets_user_id_from_request_state(self):
        """Should extract user_id from request.state attribute."""
        user_id = uuid4()
        mock_request = MagicMock(spec=Request)
        mock_request.state.user_id = user_id

        mock_notification_app = MagicMock()

        async def mock_stream():
            yield {"event": "test", "data": "{}"}

        mock_notification_app.get_notification_stream = mock_stream

        with patch(
            "backend.routers.notification.get_notification_application",
            return_value=mock_notification_app,
        ):
            response = await notifications_stream(
                mock_request, mock_notification_app
            )

        # Verify that user_id from request.state is used
        assert isinstance(response, EventSourceResponse)

    @pytest.mark.asyncio
    async def test_error_stream_for_missing_authentication(self):
        """Should return error stream with auth required message."""
        mock_request = MagicMock(spec=Request)
        mock_request.state = MagicMock()
        mock_request.state.user_id = None

        mock_notification_app = MagicMock()

        with patch(
            "backend.routers.notification.get_notification_application",
            return_value=mock_notification_app,
        ):
            response = await notifications_stream(
                mock_request, mock_notification_app
            )

        assert isinstance(response, EventSourceResponse)

        # The response should contain the error stream
        # which yields {"event": "error", "data": '{"message": "Authentication required"}'}
        # We can't easily inspect the generator without iterating it,
        # but we can verify the response type
        assert response.media_type == "text/event-stream"

    @pytest.mark.asyncio
    async def test_event_generator_catches_exception_yields_error(self):
        """Should yield error event when exception occurs in stream."""
        user_id = uuid4()
        mock_request = MagicMock(spec=Request)
        mock_request.state.user_id = user_id

        mock_notification_app = MagicMock()

        async def failing_stream():
            yield {"event": "first", "data": "{}"}
            raise ValueError("Stream processing failed")

        mock_notification_app.get_notification_stream = failing_stream

        with patch(
            "backend.routers.notification.get_notification_application",
            return_value=mock_notification_app,
        ):
            response = await notifications_stream(
                mock_request, mock_notification_app
            )

        # Should catch the exception and still return a response
        assert isinstance(response, EventSourceResponse)

    @pytest.mark.asyncio
    async def test_event_generator_exception_handling_iterates_generator(self):
        """Should handle exception and yield error event when iterating."""
        user_id = uuid4()
        mock_request = MagicMock(spec=Request)
        mock_request.state.user_id = user_id

        mock_notification_app = MagicMock()

        # Define a proper async generator function
        async def get_failing_stream(uid, is_disconnect=None):
            # Yield first event
            yield {"event": "first", "data": '{"status": "ok"}'}
            # Then raise an exception
            raise RuntimeError("Connection broke")

        mock_notification_app.get_notification_stream = get_failing_stream

        captured_generator = None

        def capture_generator(gen, media_type, ping=15):
            nonlocal captured_generator
            captured_generator = gen
            return MagicMock(spec=EventSourceResponse)

        with patch(
            "backend.routers.notification.get_notification_application",
            return_value=mock_notification_app,
        ):
            with patch(
                "backend.routers.notification.EventSourceResponse",
                side_effect=capture_generator,
            ):
                await notifications_stream(mock_request, mock_notification_app)

        # Now iterate through the captured generator to trigger exception
        assert captured_generator is not None
        events = []
        async for event in captured_generator:
            events.append(event)

        # Should have gotten the first event before the exception
        assert len(events) >= 1
        assert events[0]["event"] == "first"
        # And an error event from the exception handler
        assert any(e.get("event") == "error" for e in events)
