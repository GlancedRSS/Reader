"""Logging configuration for the application."""

import logging
import logging.handlers
import os

import structlog


def setup_logging(
    log_level: str | None = None,
    log_format: str | None = None,
) -> None:
    """Configure structlog and file logging for the application."""
    from .app import settings

    log_level = (
        log_level or os.getenv("LOG_LEVEL") or settings.log_level
    ).upper()
    log_format = (
        log_format or os.getenv("LOG_FORMAT") or settings.log_format
    ).lower()

    renderer = (
        structlog.dev.ConsoleRenderer(colors=True)
        if log_format == "text"
        else structlog.processors.JSONRenderer()
    )

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            renderer,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    if os.getenv("ENABLE_LOG_CLEANUP", "true").lower() == "true":
        _setup_file_logging(log_level)


def _setup_file_logging(log_level: str) -> None:
    """Set up rotating file handler for logs."""
    max_log_size_mb = int(os.getenv("MAX_LOG_SIZE_MB", "10"))
    max_log_size_bytes = max_log_size_mb * 1024 * 1024

    try:
        log_dir = "/logs"
        try:
            os.makedirs(log_dir, exist_ok=True)
            test_file = os.path.join(log_dir, ".write_test")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            log_path = f"{log_dir}/backend.log"
        except (OSError, PermissionError):
            log_dir = "../logs"
            os.makedirs(log_dir, exist_ok=True)
            log_path = f"{log_dir}/backend.log"
            print(f"Warning: Using fallback log directory: {log_dir}")

        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_path,
            maxBytes=max_log_size_bytes,
            backupCount=3,
            encoding="utf-8",
        )

        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )

        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)

        log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        root_logger.setLevel(log_levels.get(log_level, logging.INFO))

    except Exception as e:
        print(f"Warning: Could not set up file logging: {e}")
