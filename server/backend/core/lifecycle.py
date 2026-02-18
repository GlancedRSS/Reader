"""Application lifecycle management for startup and shutdown."""

import asyncio
from typing import Any

logger: Any = None

shutdown_event = asyncio.Event()
active_requests: set[asyncio.Task[None]] = set()
background_tasks: set[asyncio.Task[None]] = set()


async def graceful_shutdown() -> None:
    """Handle graceful shutdown by cancelling tasks and closing connections."""
    import structlog

    global logger
    if logger is None:
        logger = structlog.get_logger()

    logger.info("Initiating graceful shutdown...")

    shutdown_event.set()

    if background_tasks:
        logger.info(f"Cancelling {len(background_tasks)} background tasks...")
        for task in background_tasks:
            task.cancel()
        try:
            await asyncio.gather(*background_tasks, return_exceptions=True)
        except Exception:
            pass
        background_tasks.clear()

    if active_requests:
        logger.info(
            f"Waiting for {len(active_requests)} active requests to complete..."
        )
        try:
            await asyncio.wait_for(
                asyncio.gather(*active_requests, return_exceptions=True),
                timeout=10.0,
            )
        except TimeoutError:
            logger.warning(
                "Some requests did not complete in time, forcing shutdown"
            )

    try:
        logger.info("Closing Redis connection...")
        from ..infrastructure.external.redis import close_redis

        await close_redis()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.exception("Error closing Redis connection", error=str(e))

    try:
        logger.info("Closing database connections...")
        from .database import engine

        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.exception("Error closing database connections", error=str(e))

    logger.info("Graceful shutdown completed")


async def lifespan_init() -> None:
    """Initialize application services during startup."""
    import structlog

    global logger
    logger = structlog.get_logger()

    from ..infrastructure.external.redis import get_redis_client
    from .app import get_configuration_help, settings, validate_configuration
    from .database import init_db

    logger.info(
        "Starting Glanced Reader API server", environment=settings.environment
    )

    logger.info("Validating application configuration...")
    config_valid, config_errors = validate_configuration()
    if not config_valid:
        logger.error("Configuration validation failed:")
        for error in config_errors:
            logger.error("Configuration error", error=error)

        help_info = get_configuration_help()
        logger.error("\nConfiguration Help:")
        for env_var, help_text in help_info.items():
            if any(env_var in error for error in config_errors):
                logger.error(
                    "Configuration help", env_var=env_var, help_text=help_text
                )

        raise Exception(
            "Configuration validation failed. See logs for details."
        )

    logger.info("Configuration validation passed")

    try:
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.exception(
            "Critical: Failed to initialize database", error=str(e)
        )
        raise Exception(f"Database initialization failed: {e!s}") from None

    try:
        logger.info("Initializing Redis connection...")
        redis_client = await get_redis_client()
        await redis_client.ping()
        logger.info("Redis connection established successfully")

        try:
            await redis_client.config_set("notify-keyspace-events", "Ex")
            logger.info("Redis keyspace notifications enabled")
        except Exception as e:
            logger.warning(
                "Could not enable keyspace notifications - debounce may not work. "
                "Ensure 'notify-keyspace-events Ex' is set in redis.conf",
                error=str(e),
            )

        from ..infrastructure.notifications.notifications import (
            listen_for_timer_expirations_with_restart,
        )

        task = asyncio.create_task(listen_for_timer_expirations_with_restart())
        task.add_done_callback(background_tasks.discard)
        background_tasks.add(task)
        logger.info("Keyspace expiration listener started")

    except Exception as e:
        if settings.environment == "production":
            logger.exception(
                "Failed to initialize Redis connection", error=str(e)
            )
            raise Exception(f"Redis initialization failed: {e!s}") from None
        logger.warning(
            "Redis connection failed - continuing without caching. "
            "Features like rate limiting and SSE notifications may not work.",
            error=str(e),
        )

    logger.info("Background job system configured - jobs handled by Arq worker")


async def lifespan_shutdown() -> None:
    """Shutdown callback for application lifespan."""
    global logger
    if logger is None:
        import structlog

        logger = structlog.get_logger()
    logger.info("Initiating graceful shutdown via lifespan...")
    await graceful_shutdown()
