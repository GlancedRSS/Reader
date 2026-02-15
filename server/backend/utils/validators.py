"""Reusable validation utilities for schemas and controllers."""

from datetime import datetime, timedelta
from urllib.parse import urlparse


def validate_url(url: str) -> None:
    """Validate URL format."""
    if not url or not url.strip():
        raise ValueError("URL is required")

    try:
        parsed = urlparse(url.strip())
        if not all([parsed.scheme, parsed.netloc]):
            raise ValueError(
                "Invalid URL format. Must include scheme (http/https) and domain"
            )

        if parsed.scheme not in ["http", "https"]:
            raise ValueError("Only HTTP and HTTPS URLs are supported")

        blocked_domains = ["localhost", "127.0.0.1", "0.0.0.0"]
        if parsed.hostname in blocked_domains:
            raise ValueError(
                "Localhost and private IP addresses are not allowed"
            )

    except ValueError as e:
        if (
            "URL is required" in str(e)
            or "Only HTTP and HTTPS" in str(e)
            or "Localhost" in str(e)
        ):
            raise
        raise ValueError("Invalid URL format") from e


def validate_date_range(
    date_from: datetime | None, date_to: datetime | None
) -> None:
    """Validate date range constraints."""
    now = datetime.now()
    two_years_ago = now - timedelta(days=730)

    if date_from and date_from > now:
        raise ValueError("Start date cannot be in the future")

    if date_to and date_to > now:
        raise ValueError("End date cannot be in the future")

    if date_from and date_to:
        if date_from > date_to:
            raise ValueError("Start date cannot be after end date")

        if (date_to - date_from).days > 365:
            raise ValueError("Date range cannot exceed 1 year")

    if date_from and date_from < two_years_ago:
        raise ValueError("Start date too old. Maximum range is 2 years")


def validate_folder_name(name: str, max_length: int = 100) -> str:
    """Validate folder name."""
    if not name or not name.strip():
        raise ValueError("Folder name cannot be empty")

    name = name.strip()
    if len(name) > max_length:
        raise ValueError(f"Folder name too long (max {max_length} characters)")

    return name


def validate_opml_filename(filename: str) -> str:
    """Validate OPML filename."""
    if not filename:
        raise ValueError("No filename provided")

    if not filename.endswith(".opml"):
        raise ValueError("Invalid file format. Please upload an OPML file")

    if "/" in filename or "\\" in filename:
        raise ValueError("Invalid filename")

    return filename


def validate_file_size(
    file_size: int, max_size: int, file_type: str = "File"
) -> None:
    """Validate file size against maximum allowed."""
    if file_size > max_size:
        max_mb = max_size // (1024 * 1024)
        raise ValueError(f"{file_type} too large. Maximum size is {max_mb}MB")


def validate_batch_size(batch_size: int, max_size: int) -> None:
    """Validate batch operation size."""
    if batch_size > max_size:
        raise ValueError(
            f"Batch size ({batch_size}) exceeds maximum allowed ({max_size})"
        )
