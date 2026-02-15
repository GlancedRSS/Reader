"""Pytest configuration for unit tests."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_structlog_logger():
    """Mock structlog.get_logger to avoid NameError in tests.

    Some modules have module-level logger = structlog.get_logger() that
    can fail in test environment. This fixture ensures it's always mocked.
    """
    mock_logger = MagicMock()
    with patch("backend.infrastructure.auth.ip_utils.logger", mock_logger):
        with patch("backend.application.auth.auth.logger", mock_logger):
            yield
