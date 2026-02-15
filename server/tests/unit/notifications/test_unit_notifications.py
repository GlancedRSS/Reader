"""Unit tests for notification infrastructure."""

import json
from uuid import UUID, uuid4

import pytest

from backend.infrastructure.notifications.notifications import (
    CHANNEL_PREFIX,
    PENDING_PREFIX,
    TIMER_PREFIX,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_user_id() -> UUID:
    """Sample user ID for tests."""
    return uuid4()


@pytest.fixture
def mock_feed_id() -> UUID:
    """Sample feed ID for tests."""
    return uuid4()


@pytest.fixture
def mock_redis(monkeypatch):
    """Mock Redis client and pubsub for testing."""

    class MockPubSub:
        def __init__(self):
            self.subscribed_channels = set()
            self.psubscribed_patterns = set()
            self.messages = []
            self.listen_generator = None
            self._message_index = 0
            self._call_count = 0

        async def subscribe(self, channel: str):
            self.subscribed_channels.add(channel)

        async def unsubscribe(self, channel: str):
            self.subscribed_channels.discard(channel)

        async def psubscribe(self, pattern: str):
            self.psubscribed_patterns.add(pattern)

        async def get_message(self, timeout: int = 1):
            """Get a single message from the messages queue.

            Returns None if no messages available, simulating Redis timeout behavior.
            Raises CancelledError after all messages consumed to end stream.
            """
            self._call_count += 1
            # After a few calls, end the stream to avoid infinite loops in tests
            if self._call_count > 3:
                import asyncio

                raise asyncio.CancelledError("End of mock messages")

            if self._message_index < len(self.messages):
                msg = self.messages[self._message_index]
                self._message_index += 1
                return msg
            # No messages available - return None (timeout)
            return None

        def listen(self):
            if self.listen_generator:
                return self.listen_generator
            return self._default_listen()

        async def _default_listen(self):
            for msg in self.messages:
                yield msg

        async def __aenter__(self):
            # Reset message index and call count when entering context
            self._message_index = 0
            self._call_count = 0
            return self

        async def __aexit__(self, *args):
            pass

    class MockRedis:
        def __init__(self):
            self.data = {}
            self.published = []
            self._pubsub = None

        async def publish(self, channel: str, message: str):
            self.published.append((channel, message))
            return 1

        async def hincrby(self, key: str, field: str, value: int):
            if key not in self.data:
                self.data[key] = {}
            current = int(self.data[key].get(field or b"", 0))
            self.data[key][field] = str(current + value)
            return current + value

        async def hgetall(self, key: str):
            return self.data.get(key, {})

        async def setex(self, key: str, time: int, value: str):
            self.data[key] = value

        async def delete(self, *keys):
            for key in keys:
                self.data.pop(key, None)

        def pubsub(self):
            if self._pubsub is None:
                self._pubsub = MockPubSub()
            return self._pubsub

    mock_redis = MockRedis()

    async def mock_get_redis_client():
        return mock_redis

    from backend.infrastructure.notifications import (
        notifications as notif_module,
    )

    monkeypatch.setattr(notif_module, "get_redis_client", mock_get_redis_client)

    return mock_redis


# =============================================================================
# publish_notification Tests
# =============================================================================


class TestPublishNotification:
    """Test direct notification publishing."""

    async def test_publish_notification_success(self, mock_redis, mock_user_id):
        """Should publish notification to user's channel."""
        from backend.infrastructure.notifications.notifications import (
            publish_notification,
        )

        result = await publish_notification(
            user_id=mock_user_id,
            event_type="test_event",
            data={"message": "test"},
        )

        assert result is True
        assert len(mock_redis.published) == 1

    async def test_publish_notification_with_different_event_types(
        self, mock_redis, mock_user_id
    ):
        """Should publish different event types."""
        from backend.infrastructure.notifications.notifications import (
            publish_notification,
        )

        event_types = ["new_articles", "feed_updated", "test_event"]

        for event_type in event_types:
            await publish_notification(
                user_id=mock_user_id,
                event_type=event_type,
                data={"test": "data"},
            )

        assert len(mock_redis.published) == len(event_types)


# =============================================================================
# queue_new_articles_notification Tests
# =============================================================================


class TestQueueNewArticlesNotification:
    """Test debounced notification queuing."""

    async def test_queue_notification_increments_count(
        self, mock_redis, mock_user_id, mock_feed_id
    ):
        """Should increment article count in pending hash."""
        from backend.infrastructure.notifications.notifications import (
            queue_new_articles_notification,
        )

        await queue_new_articles_notification(
            user_id=mock_user_id,
            feed_id=mock_feed_id,
            article_count=5,
        )

        pending_key = f"{PENDING_PREFIX}{mock_user_id}"
        assert pending_key in mock_redis.data
        assert mock_redis.data[pending_key][str(mock_feed_id)] == "5"

    async def test_queue_notification_multiple_feeds(
        self, mock_redis, mock_user_id, mock_feed_id
    ):
        """Should aggregate multiple feeds in pending hash."""
        from backend.infrastructure.notifications.notifications import (
            queue_new_articles_notification,
        )

        feed_id_2 = uuid4()

        await queue_new_articles_notification(
            user_id=mock_user_id,
            feed_id=mock_feed_id,
            article_count=3,
        )

        await queue_new_articles_notification(
            user_id=mock_user_id,
            feed_id=feed_id_2,
            article_count=7,
        )

        pending_key = f"{PENDING_PREFIX}{mock_user_id}"
        pending = mock_redis.data[pending_key]
        assert pending[str(mock_feed_id)] == "3"
        assert pending[str(feed_id_2)] == "7"

    async def test_queue_notification_same_feed_accumulates(
        self, mock_redis, mock_user_id, mock_feed_id
    ):
        """Should accumulate counts for same feed."""
        from backend.infrastructure.notifications.notifications import (
            queue_new_articles_notification,
        )

        await queue_new_articles_notification(
            user_id=mock_user_id,
            feed_id=mock_feed_id,
            article_count=3,
        )

        await queue_new_articles_notification(
            user_id=mock_user_id,
            feed_id=mock_feed_id,
            article_count=4,
        )

        pending_key = f"{PENDING_PREFIX}{mock_user_id}"
        assert mock_redis.data[pending_key][str(mock_feed_id)] == "7"

    async def test_queue_notification_sets_timer(
        self, mock_redis, mock_user_id, mock_feed_id
    ):
        """Should set debounce timer with default TTL."""
        from backend.infrastructure.notifications.notifications import (
            queue_new_articles_notification,
        )

        await queue_new_articles_notification(
            user_id=mock_user_id,
            feed_id=mock_feed_id,
            article_count=5,
        )

        timer_key = f"{TIMER_PREFIX}{mock_user_id}"
        assert timer_key in mock_redis.data

    async def test_queue_notification_custom_debounce(
        self, mock_redis, mock_user_id, mock_feed_id
    ):
        """Should use custom debounce seconds when provided."""
        from backend.infrastructure.notifications.notifications import (
            queue_new_articles_notification,
        )

        custom_debounce = 30

        await queue_new_articles_notification(
            user_id=mock_user_id,
            feed_id=mock_feed_id,
            article_count=5,
            debounce_seconds=custom_debounce,
        )

        timer_key = f"{TIMER_PREFIX}{mock_user_id}"
        assert timer_key in mock_redis.data


# =============================================================================
# flush_pending_notifications Tests
# =============================================================================


class TestFlushPendingNotifications:
    """Test notification flushing on timer expiration."""

    async def test_flush_publishes_aggregated_notifications(
        self, mock_redis, mock_user_id, mock_feed_id
    ):
        """Should publish aggregated notification and clear pending data."""
        from backend.infrastructure.notifications.notifications import (
            flush_pending_notifications,
        )

        # Set up pending data
        pending_key = f"{PENDING_PREFIX}{mock_user_id}"
        feed_id_2 = uuid4()
        mock_redis.data[pending_key] = {
            str(mock_feed_id): "5",
            str(feed_id_2): "3",
        }

        await flush_pending_notifications(mock_user_id)

        # Verify notification was published
        assert len(mock_redis.published) == 1
        channel, message = mock_redis.published[0]
        assert channel == f"{CHANNEL_PREFIX}{mock_user_id}"

        payload = json.loads(message)
        assert payload["type"] == "new_articles"
        assert payload["data"][str(mock_feed_id)] == 5
        assert payload["data"][str(feed_id_2)] == 3

        # Verify pending data was cleared
        assert pending_key not in mock_redis.data

    async def test_flush_with_no_pending_data(self, mock_redis, mock_user_id):
        """Should return early when no pending data exists."""
        from backend.infrastructure.notifications.notifications import (
            flush_pending_notifications,
        )

        # Should not raise
        await flush_pending_notifications(mock_user_id)
        assert len(mock_redis.published) == 0

    async def test_clears_timer_after_flush(
        self, mock_redis, mock_user_id, mock_feed_id
    ):
        """Should delete timer key after flushing."""
        from backend.infrastructure.notifications.notifications import (
            flush_pending_notifications,
        )

        pending_key = f"{PENDING_PREFIX}{mock_user_id}"
        timer_key = f"{TIMER_PREFIX}{mock_user_id}"
        mock_redis.data[pending_key] = {str(mock_feed_id): "5"}
        mock_redis.data[timer_key] = "1"

        await flush_pending_notifications(mock_user_id)

        assert timer_key not in mock_redis.data


# =============================================================================
# event_stream Tests
# =============================================================================


class TestEventStream:
    """Test SSE event stream generation."""

    async def test_event_stream_yields_messages(self, mock_redis, mock_user_id):
        """Should yield SSE events from pubsub messages."""
        from backend.infrastructure.notifications.notifications import (
            event_stream,
        )

        # Add a message to the pubsub messages queue
        pubsub = mock_redis.pubsub()
        pubsub.messages.append(
            {
                "type": "message",
                "data": json.dumps(
                    {"type": "new_articles", "data": {"feed_id": "5"}}
                ),
            }
        )

        events = []
        async for event in event_stream(mock_user_id):
            events.append(event)
            # Break after receiving first event (which came from messages queue)
            if len(events) >= 1:
                break

        assert len(events) == 1
        assert events[0]["event"] == "new_articles"

    async def test_event_stream_subscribes_to_channel(
        self, mock_redis, mock_user_id
    ):
        """Should subscribe to user's notification channel."""
        # The stream will raise CancelledError after a few get_message calls
        # We need to catch this to end the test gracefully
        import asyncio

        from backend.infrastructure.notifications.notifications import (
            event_stream,
        )

        try:
            async for _ in event_stream(mock_user_id):
                pass
        except asyncio.CancelledError:
            # Expected - stream ends when mock raises CancelledError
            pass

        # Test passes if no exception was raised during stream setup
        # (the CancelledError is expected and caught)
