from arq.connections import RedisSettings
from arq.cron import CronJob
from arq.worker import func

from backend.core.app import settings
from backend.workers.functions import (
    scheduled_auto_mark_read,
    scheduled_feed_cleanup,
    scheduled_feed_refresh,
    shutdown,
    startup,
)


def get_redis_settings() -> RedisSettings:
    redis_url = settings.redis_url or "redis://localhost:6379"
    return RedisSettings.from_dsn(redis_url)


class WorkerSettings:
    redis_settings = get_redis_settings()

    functions = [
        func("backend.workers.functions.opml_import", name="opml_import"),
        func("backend.workers.functions.opml_export", name="opml_export"),
        func(
            "backend.workers.functions.feed_create_and_subscribe",
            name="feed_create_and_subscribe",
        ),
    ]

    cron_jobs = [
        CronJob(
            name="scheduled_feed_refresh",
            coroutine=scheduled_feed_refresh,
            month=None,
            day=None,
            weekday=None,
            hour=None,
            minute=set(range(0, 60, 15)),
            second=0,
            microsecond=0,
            run_at_startup=False,
            unique=False,
            job_id=None,
            timeout_s=None,
            keep_result_s=None,
            keep_result_forever=None,
            max_tries=None,
        ),
        CronJob(
            name="scheduled_feed_cleanup",
            coroutine=scheduled_feed_cleanup,
            month=None,
            day=None,
            weekday=None,
            hour=2,
            minute=0,
            second=0,
            microsecond=0,
            run_at_startup=False,
            unique=False,
            job_id=None,
            timeout_s=None,
            keep_result_s=None,
            keep_result_forever=None,
            max_tries=None,
        ),
        CronJob(
            name="scheduled_auto_mark_read",
            coroutine=scheduled_auto_mark_read,
            month=None,
            day=None,
            weekday=None,
            hour=3,
            minute=0,
            second=0,
            microsecond=0,
            run_at_startup=False,
            unique=False,
            job_id=None,
            timeout_s=None,
            keep_result_s=None,
            keep_result_forever=None,
            max_tries=None,
        ),
    ]

    on_startup = startup
    on_shutdown = shutdown
    job_timeout = 3600
    max_jobs = 10
    poll_delay = 0.5
    queue_name = "arq:queue"
    max_tries = 3
    allow_select_jobs = True
    use_uvloop = True
    result_expires = 3600
