"""Server-Sent Events (SSE) notifications using Redis pub/sub and keyspace notifications."""

import asyncio
import json
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any, cast
from uuid import UUID

import structlog

from backend.infrastructure.external.redis import get_redis_client

logger = structlog.get_logger()

CHANNEL_PREFIX = "notifications:user:"
PENDING_PREFIX = "notifications:pending:user:"
TIMER_PREFIX = "notifications:timer:user:"
DEBOUNCE_SECONDS = 60


async def publish_notification(
    user_id: UUID, event_type: str, data: dict[str, Any]
) -> bool:
    """Publish a notification to a user's Redis channel."""
    try:
        redis_client = await get_redis_client()
        channel = f"{CHANNEL_PREFIX}{user_id}"

        message = json.dumps(
            {
                "type": event_type,
                "data": data,
            }
        )

        await redis_client.publish(channel, message)
        logger.info(
            "Notification published",
            user_id=user_id,
            event_type=event_type,
            channel=channel,
        )
        return True
    except Exception as e:
        logger.exception(
            "Failed to publish notification",
            user_id=user_id,
            event_type=event_type,
            error=str(e),
        )
        return False


async def queue_new_articles_notification(
    user_id: UUID,
    feed_id: UUID,
    article_count: int,
    debounce_seconds: int = DEBOUNCE_SECONDS,
) -> None:
    """Queue a notification for new articles (debounced)."""
    redis_client = await get_redis_client()

    pending_key = f"{PENDING_PREFIX}{user_id}"
    timer_key = f"{TIMER_PREFIX}{user_id}"

    await cast(
        "Awaitable[int]",
        redis_client.hincrby(pending_key, str(feed_id), article_count),
    )

    await redis_client.setex(timer_key, debounce_seconds, "1")

    logger.debug(
        "Queued debounced notification",
        user_id=user_id,
        feed_id=feed_id,
        article_count=article_count,
    )


async def event_stream(
    user_id: UUID, is_disconnect: Callable[[], Awaitable[bool]] | None = None
) -> AsyncIterator[dict[str, str]]:
    """Subscribe to a user's notification channel and yield SSE events."""
    redis_client = await get_redis_client()
    channel = f"{CHANNEL_PREFIX}{user_id}"

    async with redis_client.pubsub() as pubsub:
        await pubsub.subscribe(channel)
        logger.info(
            "SSE connection established", user_id=user_id, channel=channel
        )

        try:
            while True:
                if is_disconnect is not None and await is_disconnect():
                    logger.info(
                        "Client disconnected, closing SSE stream",
                        user_id=user_id,
                        channel=channel,
                    )
                    break

                message = await pubsub.get_message(timeout=1)

                if message is None:
                    continue

                if message["type"] == "message":
                    try:
                        payload = json.loads(message["data"])
                        yield {
                            "event": payload["type"],
                            "data": json.dumps(payload["data"]),
                        }
                    except json.JSONDecodeError:
                        logger.warning(
                            "Invalid JSON in notification message",
                            user_id=user_id,
                            message=message["data"],
                        )
                        continue
                    except Exception as e:
                        logger.exception(
                            "Error processing notification",
                            user_id=user_id,
                            error=str(e),
                        )
                        continue
        except asyncio.CancelledError:
            logger.info(
                "SSE stream cancelled", user_id=user_id, channel=channel
            )
            raise
        except Exception as e:
            logger.exception(
                "SSE stream error",
                user_id=user_id,
                error=str(e),
            )
        finally:
            await pubsub.unsubscribe(channel)
            logger.info(
                "SSE connection closed", user_id=user_id, channel=channel
            )


async def flush_pending_notifications(user_id: UUID) -> None:
    """Flush all pending notifications for a user and publish aggregated SSE event."""
    redis_client = await get_redis_client()

    pending_key = f"{PENDING_PREFIX}{user_id}"
    timer_key = f"{TIMER_PREFIX}{user_id}"

    pending_data = await cast(
        "Awaitable[dict[str, str]]",
        redis_client.hgetall(pending_key),
    )

    if not pending_data:
        return

    feed_counts = {}
    for feed_id_str, count_str in pending_data.items():
        if isinstance(feed_id_str, bytes):
            feed_id_str = feed_id_str.decode()
        if isinstance(count_str, bytes):
            count_str = count_str.decode()
        feed_counts[feed_id_str] = int(count_str)

    await publish_notification(user_id, "new_articles", feed_counts)

    await redis_client.delete(pending_key, timer_key)

    logger.info(
        "Flushed pending notifications",
        user_id=user_id,
        feed_count=len(feed_counts),
        total_articles=sum(feed_counts.values()),
    )


async def listen_for_timer_expirations() -> None:
    """Listen for Redis keyspace expiration events and flush pending notifications."""
    from backend.core.app import settings

    redis_client = await get_redis_client()

    db = settings.redis_keyspace_db
    async with redis_client.pubsub() as pubsub:
        await pubsub.psubscribe(f"__keyevent@{db}__:expired")
        logger.info(
            "Keyspace expiration listener started",
            db=db,
        )

        try:
            async for message in pubsub.listen():
                if message["type"] == "pmessage":
                    key = message.get("data")
                    if key and isinstance(key, bytes):
                        key = key.decode()
                    if key and key.startswith(TIMER_PREFIX):
                        user_id_str = key.removeprefix(TIMER_PREFIX)
                        try:
                            user_id = UUID(user_id_str)
                            await flush_pending_notifications(user_id)
                        except ValueError:
                            logger.warning(
                                "Invalid user_id in timer expiration",
                                key=key,
                                user_id_str=user_id_str,
                            )
        except asyncio.CancelledError:
            logger.info("Keyspace expiration listener cancelled")
            raise
        except Exception as e:
            logger.exception(
                "Keyspace expiration listener error",
                error=str(e),
            )
            raise


async def listen_for_timer_expirations_with_restart() -> None:
    """Run the keyspace listener and restart it on crash."""
    import traceback

    while True:
        try:
            await listen_for_timer_expirations()
        except asyncio.CancelledError:
            logger.info("Keyspace expiration listener shutdown requested")
            break
        except Exception as e:
            logger.exception(
                "Keyspace expiration listener crashed, restarting in 5 seconds...",
                error=str(e),
                traceback=traceback.format_exc(),
            )
            await asyncio.sleep(5)
