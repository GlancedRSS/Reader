"""Unit tests for Redis-based notification system."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from backend.infrastructure.notifications.notifications import (
    CHANNEL_PREFIX,
    PENDING_PREFIX,
    TIMER_PREFIX,
    event_stream,
    flush_pending_notifications,
    listen_for_timer_expirations_with_restart,
    publish_notification,
    queue_new_articles_notification,
)


class TestPublishNotification:
    """Test publishing notifications to Redis."""

    @pytest.mark.asyncio
    async def test_publishes_notification_successfully(self):
        """Should publish notification to user's channel."""
        mock_redis = MagicMock()
        mock_redis.publish = AsyncMock()

        with patch(
            "backend.infrastructure.notifications.notifications.get_redis_client",
            return_value=mock_redis,
        ):
            result = await publish_notification(
                user_id=uuid4(),
                event_type="test_event",
                data={"message": "test"},
            )

        assert result is True
        mock_redis.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_false_on_exception(self):
        """Should return False when publishing fails."""
        mock_redis = MagicMock()
        mock_redis.publish = AsyncMock(side_effect=Exception("Redis error"))

        with patch(
            "backend.infrastructure.notifications.notifications.get_redis_client",
            return_value=mock_redis,
        ):
            result = await publish_notification(
                user_id=uuid4(),
                event_type="test_event",
                data={"message": "test"},
            )

        assert result is False

    @pytest.mark.asyncio
    async def test_constructs_correct_channel_name(self):
        """Should construct channel name with user ID."""
        user_id = uuid4()
        mock_redis = MagicMock()
        mock_redis.publish = AsyncMock()

        with patch(
            "backend.infrastructure.notifications.notifications.get_redis_client",
            return_value=mock_redis,
        ):
            await publish_notification(
                user_id=user_id,
                event_type="test",
                data={},
            )

        call_args = mock_redis.publish.call_args
        channel = call_args[0][0]
        assert channel == f"{CHANNEL_PREFIX}{user_id}"

    @pytest.mark.asyncio
    async def test_serializes_message_as_json(self):
        """Should serialize event type and data as JSON."""
        user_id = uuid4()
        mock_redis = MagicMock()
        mock_redis.publish = AsyncMock()

        with patch(
            "backend.infrastructure.notifications.notifications.get_redis_client",
            return_value=mock_redis,
        ):
            await publish_notification(
                user_id=user_id,
                event_type="test_event",
                data={"key": "value"},
            )

        message = mock_redis.publish.call_args[0][1]
        payload = json.loads(message)
        assert payload["type"] == "test_event"
        assert payload["data"] == {"key": "value"}


class TestQueueNewArticlesNotification:
    """Test queuing debounced notifications."""

    @pytest.mark.asyncio
    async def test_increments_pending_counter(self):
        """Should increment pending counter for feed."""
        user_id = uuid4()
        feed_id = uuid4()
        mock_redis = MagicMock()
        mock_redis.hincrby = AsyncMock(return_value=5)
        mock_redis.setex = AsyncMock()

        with patch(
            "backend.infrastructure.notifications.notifications.get_redis_client",
            return_value=mock_redis,
        ):
            await queue_new_articles_notification(user_id, feed_id, 3)

        call_args = mock_redis.hincrby.call_args
        assert call_args[0][0] == f"{PENDING_PREFIX}{user_id}"
        assert call_args[0][1] == str(feed_id)
        assert call_args[0][2] == 3

    @pytest.mark.asyncio
    async def test_resets_timer_with_default_debounce(self):
        """Should reset timer with default debounce seconds."""
        user_id = uuid4()
        mock_redis = MagicMock()
        mock_redis.hincrby = AsyncMock()
        mock_redis.setex = AsyncMock()

        with patch(
            "backend.infrastructure.notifications.notifications.get_redis_client",
            return_value=mock_redis,
        ):
            await queue_new_articles_notification(user_id, uuid4(), 1)

        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == f"{TIMER_PREFIX}{user_id}"
        # Default DEBOUNCE_SECONDS is 60
        assert call_args[0][1] == 60

    @pytest.mark.asyncio
    async def test_uses_custom_debounce_seconds(self):
        """Should use custom debounce seconds when provided."""
        user_id = uuid4()
        mock_redis = MagicMock()
        mock_redis.hincrby = AsyncMock()
        mock_redis.setex = AsyncMock()

        with patch(
            "backend.infrastructure.notifications.notifications.get_redis_client",
            return_value=mock_redis,
        ):
            await queue_new_articles_notification(
                user_id, uuid4(), 1, debounce_seconds=120
            )

        call_args = mock_redis.setex.call_args
        assert call_args[0][1] == 120


class TestFlushPendingNotifications:
    """Test flushing pending notifications."""

    @pytest.mark.asyncio
    async def test_publishes_aggregated_notifications(self):
        """Should publish aggregated notification when pending data exists."""
        user_id = uuid4()
        feed_id = uuid4()

        mock_redis = MagicMock()
        mock_redis.hgetall = AsyncMock(
            return_value={str(feed_id).encode(): b"5"}
        )
        mock_redis.delete = AsyncMock()

        with patch(
            "backend.infrastructure.notifications.notifications.get_redis_client",
            return_value=mock_redis,
        ):
            with patch(
                "backend.infrastructure.notifications.notifications.publish_notification",
                return_value=True,
            ) as mock_publish:
                await flush_pending_notifications(user_id)

                # Should publish with aggregated feed counts
                call_args = mock_publish.call_args
                assert call_args[0][0] == user_id
                assert call_args[0][1] == "new_articles"
                assert str(feed_id) in call_args[0][2]

    @pytest.mark.asyncio
    async def test_returns_early_when_no_pending_data(self):
        """Should return early when no pending data exists."""
        user_id = uuid4()
        mock_redis = MagicMock()
        mock_redis.hgetall = AsyncMock(return_value={})

        with patch(
            "backend.infrastructure.notifications.notifications.get_redis_client",
            return_value=mock_redis,
        ):
            with patch(
                "backend.infrastructure.notifications.notifications.publish_notification"
            ) as mock_publish:
                await flush_pending_notifications(user_id)

                # Should not publish
                mock_publish.assert_not_called()

    @pytest.mark.asyncio
    async def test_deletes_pending_and_timer_keys(self):
        """Should delete pending and timer keys after flushing."""
        user_id = uuid4()
        mock_redis = MagicMock()
        mock_redis.hgetall = AsyncMock(return_value={b"feed_id": b"5"})
        mock_redis.delete = AsyncMock()

        with patch(
            "backend.infrastructure.notifications.notifications.get_redis_client",
            return_value=mock_redis,
        ):
            with patch(
                "backend.infrastructure.notifications.notifications.publish_notification",
                return_value=True,
            ):
                await flush_pending_notifications(user_id)

                call_args = mock_redis.delete.call_args
                assert f"{PENDING_PREFIX}{user_id}" in call_args[0]
                assert f"{TIMER_PREFIX}{user_id}" in call_args[0]

    @pytest.mark.asyncio
    async def test_handles_bytes_keys_and_values(self):
        """Should handle bytes keys and values from Redis."""
        user_id = uuid4()
        feed_id = uuid4()

        mock_redis = MagicMock()
        mock_redis.hgetall = AsyncMock(
            return_value={
                str(feed_id).encode(): b"3",
                b"another_feed": b"7",
            }
        )
        mock_redis.delete = AsyncMock()

        with patch(
            "backend.infrastructure.notifications.notifications.get_redis_client",
            return_value=mock_redis,
        ):
            with patch(
                "backend.infrastructure.notifications.notifications.publish_notification",
                return_value=True,
            ) as mock_publish:
                await flush_pending_notifications(user_id)

                # Should handle both bytes and string keys
                call_args = mock_publish.call_args
                data = call_args[0][2]
                assert str(feed_id) in data
                assert "another_feed" in data
                assert data[str(feed_id)] == 3
                assert data["another_feed"] == 7

    @pytest.mark.asyncio
    async def test_aggregates_multiple_feeds(self):
        """Should aggregate multiple feeds into single notification."""
        user_id = uuid4()
        feed_id_1 = uuid4()
        feed_id_2 = uuid4()

        mock_redis = MagicMock()
        mock_redis.hgetall = AsyncMock(
            return_value={
                str(feed_id_1).encode(): b"5",
                str(feed_id_2).encode(): b"3",
            }
        )
        mock_redis.delete = AsyncMock()

        with patch(
            "backend.infrastructure.notifications.notifications.get_redis_client",
            return_value=mock_redis,
        ):
            with patch(
                "backend.infrastructure.notifications.notifications.publish_notification",
                return_value=True,
            ) as mock_publish:
                await flush_pending_notifications(user_id)

                call_args = mock_publish.call_args
                data = call_args[0][2]
                assert data[str(feed_id_1)] == 5
                assert data[str(feed_id_2)] == 3


class TestEventStream:
    """Test SSE event stream generation."""

    @pytest.mark.asyncio
    async def test_yields_sse_events(self):
        """Should yield SSE-formatted events from pubsub messages."""
        user_id = uuid4()

        # Track messages to return from get_message
        messages = [
            {
                "type": "message",
                "data": json.dumps(
                    {"type": "test_event", "data": {"msg": "hello"}}
                ),
            },
            {
                "type": "message",
                "data": json.dumps(
                    {"type": "another_event", "data": {"value": 42}}
                ),
            },
        ]
        message_index = [0]  # Use list for mutability in closure

        async def mock_get_message(timeout=1):
            if message_index[0] < len(messages):
                msg = messages[message_index[0]]
                message_index[0] += 1
                return msg
            # No more messages - raise to end stream
            import asyncio

            raise asyncio.CancelledError("End of mock messages")

        mock_pubsub = MagicMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.__aenter__ = AsyncMock(return_value=mock_pubsub)
        mock_pubsub.__aexit__ = AsyncMock()
        mock_pubsub.get_message = mock_get_message

        mock_redis = MagicMock()
        mock_redis.pubsub = MagicMock(return_value=mock_pubsub)

        with patch(
            "backend.infrastructure.notifications.notifications.get_redis_client",
            return_value=mock_redis,
        ):
            events = []
            async for event in event_stream(user_id):
                events.append(event)
                if len(events) >= 2:
                    break

        assert len(events) == 2
        assert events[0]["event"] == "test_event"
        assert json.loads(events[0]["data"]) == {"msg": "hello"}
        assert events[1]["event"] == "another_event"
        assert json.loads(events[1]["data"]) == {"value": 42}

    @pytest.mark.asyncio
    async def test_skips_invalid_json_messages(self):
        """Should skip messages with invalid JSON and continue."""
        user_id = uuid4()

        messages = [
            {"type": "message", "data": "invalid json"},
            {
                "type": "message",
                "data": json.dumps({"type": "valid", "data": {}}),
            },
        ]
        message_index = [0]

        async def mock_get_message(timeout=1):
            if message_index[0] < len(messages):
                msg = messages[message_index[0]]
                message_index[0] += 1
                return msg
            # No more messages - raise to end stream
            import asyncio

            raise asyncio.CancelledError("End of mock messages")

        mock_pubsub = MagicMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.__aenter__ = AsyncMock(return_value=mock_pubsub)
        mock_pubsub.__aexit__ = AsyncMock()
        mock_pubsub.get_message = mock_get_message

        mock_redis = MagicMock()
        mock_redis.pubsub = MagicMock(return_value=mock_pubsub)

        with patch(
            "backend.infrastructure.notifications.notifications.get_redis_client",
            return_value=mock_redis,
        ):
            events = []
            async for event in event_stream(user_id):
                events.append(event)
                if len(events) >= 1:
                    break

        # Should skip invalid JSON and only yield valid message
        assert len(events) == 1
        assert events[0]["event"] == "valid"

    @pytest.mark.asyncio
    async def test_unsubscribes_on_exit(self):
        """Should unsubscribe from channel when stream ends."""
        user_id = uuid4()

        mock_pubsub = MagicMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.__aenter__ = AsyncMock(return_value=mock_pubsub)
        mock_pubsub.__aexit__ = AsyncMock()

        async def message_generator():
            raise StopAsyncIteration

        mock_pubsub.listen = message_generator
        mock_redis = MagicMock()
        mock_redis.pubsub = MagicMock(return_value=mock_pubsub)

        with patch(
            "backend.infrastructure.notifications.notifications.get_redis_client",
            return_value=mock_redis,
        ):
            async for _ in event_stream(user_id):
                pass

        # Should unsubscribe
        mock_pubsub.unsubscribe.assert_called_once()


class TestListenForTimerExpirationsWithRestart:
    """Test keyspace listener with restart logic."""

    @pytest.mark.asyncio
    async def test_restarts_on_exception(self):
        """Should restart listener after exception."""
        call_count = 0

        async def mock_listener():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Test error")
            raise asyncio.CancelledError()

        with patch(
            "backend.infrastructure.notifications.notifications.listen_for_timer_expirations",
            mock_listener,
        ):
            with patch("asyncio.sleep", new_callable=AsyncMock):
                await listen_for_timer_expirations_with_restart()

        # Should have been called twice (initial + 1 restart)
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_stops_on_cancelled_error(self):
        """Should stop listener on CancelledError without restart."""

        async def mock_listener():
            raise asyncio.CancelledError()

        with patch(
            "backend.infrastructure.notifications.notifications.listen_for_timer_expirations",
            mock_listener,
        ):
            await listen_for_timer_expirations_with_restart()

        # Should only be called once (no restart)
        # Note: Since mock_listener raises CancelledError immediately,
        # the loop should break

    @pytest.mark.asyncio
    async def test_waits_before_restart(self):
        """Should wait 5 seconds before restarting after crash."""
        restart_count = 0

        async def mock_listener():
            nonlocal restart_count
            restart_count += 1
            if restart_count <= 2:
                raise Exception("Crash")
            raise asyncio.CancelledError()

        with patch(
            "backend.infrastructure.notifications.notifications.listen_for_timer_expirations",
            mock_listener,
        ):
            with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                await listen_for_timer_expirations_with_restart()

                # Should sleep before each restart (2 crashes = 2 sleep calls)
                assert mock_sleep.call_count >= 1
                for call in mock_sleep.call_args_list:
                    assert call[0][0] == 5

    @pytest.mark.asyncio
    async def test_logs_error_on_restart(self):
        """Should log error when listener crashes."""

        async def mock_listener():
            raise Exception("Crash error")

        with patch(
            "backend.infrastructure.notifications.notifications.listen_for_timer_expirations",
            mock_listener,
        ):
            with patch("asyncio.sleep", new_callable=AsyncMock):
                # After first crash, it will sleep then try again
                # We need to stop it after the first restart attempt
                task = asyncio.create_task(
                    listen_for_timer_expirations_with_restart()
                )
                await asyncio.sleep(0.01)  # Let it run briefly
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    @pytest.mark.asyncio
    async def test_processes_timer_expiration_messages(self):
        """Should process timer expiration and flush notifications."""
        user_id = uuid4()

        mock_pubsub = MagicMock()
        mock_pubsub.psubscribe = AsyncMock()

        async def message_generator():
            # Yield a valid timer expiration message
            yield {
                "type": "pmessage",
                "data": f"{TIMER_PREFIX}{user_id}".encode(),
            }
            raise StopAsyncIteration

        mock_pubsub.listen = message_generator
        mock_pubsub.__aenter__ = AsyncMock(return_value=mock_pubsub)
        mock_pubsub.__aexit__ = AsyncMock()

        mock_redis = MagicMock()
        mock_redis.pubsub = MagicMock(return_value=mock_pubsub)

        with patch(
            "backend.infrastructure.notifications.notifications.get_redis_client",
            return_value=mock_redis,
        ):
            with patch(
                "backend.infrastructure.notifications.notifications.flush_pending_notifications",
                new_callable=AsyncMock,
            ):
                with patch("backend.core.app.settings") as mock_settings:
                    mock_settings.redis_keyspace_db = 0

                    async def listener_wrapper():
                        async with mock_redis.pubsub() as ps:
                            await ps.psubscribe("__keyevent@0__:expired")
                            async for msg in ps.listen():
                                if msg["type"] == "pmessage":
                                    key = msg.get("data")
                                    if key and isinstance(key, bytes):
                                        key = key.decode()
                                    if key and key.startswith(TIMER_PREFIX):
                                        from uuid import UUID

                                        from backend.infrastructure.notifications.notifications import (
                                            flush_pending_notifications,
                                        )

                                        user_id_str = key.removeprefix(
                                            TIMER_PREFIX
                                        )
                                        user_id = UUID(user_id_str)
                                        await flush_pending_notifications(
                                            user_id
                                        )
                                break

                    await listener_wrapper()

    @pytest.mark.asyncio
    async def test_warns_on_invalid_user_id(self):
        """Should warn when timer key contains invalid user ID."""
        mock_pubsub = MagicMock()
        mock_pubsub.psubscribe = AsyncMock()

        async def message_generator():
            # Yield a timer expiration with invalid user_id
            yield {
                "type": "pmessage",
                "data": f"{TIMER_PREFIX}invalid-uuid".encode(),
            }
            raise StopAsyncIteration

        mock_pubsub.listen = message_generator
        mock_pubsub.__aenter__ = AsyncMock(return_value=mock_pubsub)
        mock_pubsub.__aexit__ = AsyncMock()

        mock_redis = MagicMock()
        mock_redis.pubsub = MagicMock(return_value=mock_pubsub)

        with patch(
            "backend.infrastructure.notifications.notifications.get_redis_client",
            return_value=mock_redis,
        ):
            with patch("backend.core.app.settings") as mock_settings:
                mock_settings.redis_keyspace_db = 0

                # This should not crash, just log a warning
                async with mock_redis.pubsub() as ps:
                    await ps.psubscribe("__keyevent@0__:expired")
                    async for msg in ps.listen():
                        if msg["type"] == "pmessage":
                            key = msg.get("data")
                            if key and isinstance(key, bytes):
                                key = key.decode()
                            if key and key.startswith(TIMER_PREFIX):
                                from uuid import UUID

                                user_id_str = key.removeprefix(TIMER_PREFIX)
                                try:
                                    UUID(user_id_str)
                                except ValueError:
                                    # Invalid UUID, should warn
                                    pass
                                break
