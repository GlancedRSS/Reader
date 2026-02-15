"""Unit tests for core application configuration."""

from unittest.mock import MagicMock, patch

from backend.core.app import (
    Settings,
    get_configuration_help,
    validate_configuration,
)


class TestSettings:
    """Test Settings class."""

    def test_default_values(self):
        """Should have correct default values."""
        s = Settings()
        # Environment defaults to "production" in Field, but .env files may override
        assert s.host == "0.0.0.0"
        assert s.port == 2076
        # Version changes frequently, just check it's set
        assert s.version
        assert isinstance(s.version, str)
        # User agent should contain version, project name and repo URL
        assert "Glanced-Reader" in s.user_agent
        assert s.version in s.user_agent
        assert "github.com/glancedrss/reader" in s.user_agent
        assert s.request_timeout == 30
        assert s.max_concurrent_feeds == 50
        # feed_refresh_interval_minutes is overridden by .env files, skip check
        assert s.feed_refresh_batch_size == 10
        assert s.max_feed_size_mb == 5

    def test_database_url_default(self):
        """Should have default database URL."""
        s = Settings()
        assert "postgresql://" in s.database_url
        assert "localhost:5432" in s.database_url

    def test_is_development_property(self):
        """Should correctly identify development mode."""
        s = Settings(environment="development")
        assert s.is_development is True

        s = Settings(environment="production")
        assert s.is_development is False

    def test_is_development_case_insensitive(self):
        """Should be case-insensitive for environment check."""
        s = Settings(environment="DEVELOPMENT")
        assert s.is_development is True

        s = Settings(environment="Development")
        assert s.is_development is True

    def test_session_cookie_max_age_property(self):
        """Should calculate max age in seconds."""
        s = Settings(session_timeout_days=7)
        assert s.session_cookie_max_age == 7 * 24 * 60 * 60

        s = Settings(session_timeout_days=30)
        assert s.session_cookie_max_age == 30 * 24 * 60 * 60

    def test_session_cookie_secure_effective_development(self):
        """Should return False for development mode."""
        s = Settings(environment="development", cookie_secure=None)
        assert s.session_cookie_secure_effective is False

    def test_session_cookie_secure_effective_production(self):
        """Should return True for production mode by default."""
        s = Settings(
            environment="production",
            cookie_secure=None,
            session_cookie_secure=True,
        )
        assert s.session_cookie_secure_effective is True

    def test_session_cookie_secure_effective_override(self):
        """Should respect override value."""
        s = Settings(environment="development", cookie_secure=True)
        assert s.session_cookie_secure_effective is True

        s = Settings(environment="production", cookie_secure=False)
        assert s.session_cookie_secure_effective is False

    def test_storage_config_property(self):
        """Should return storage configuration dictionary."""
        s = Settings(
            storage_path="/data/storage",
        )
        config = s.storage_config
        assert config["path"] == "/data/storage"

    def test_redis_defaults(self):
        """Should have correct Redis defaults."""
        s = Settings()
        assert "redis://localhost:6379" in s.redis_url
        assert s.redis_max_connections == 50
        assert s.redis_keyspace_db == 0

    def test_cookie_settings_defaults(self):
        """Should have correct cookie defaults."""
        s = Settings()
        assert s.session_timeout_days == 30
        assert s.session_cookie_name == "session_id"
        assert s.session_cookie_secure is True
        assert s.session_cookie_httponly is True
        assert s.session_cookie_samesite == "lax"
        assert s.csrf_cookie_name == "csrf_token"
        assert s.csrf_token_length == 32

    def test_opml_settings_defaults(self):
        """Should have correct OPML defaults."""
        s = Settings()
        assert s.opml_max_file_size == 16 * 1024 * 1024  # 16MB
        assert s.opml_max_folder_depth == 9
        assert s.opml_import_timeout_seconds == 300  # 5 minutes


class TestValidateConfiguration:
    """Test configuration validation."""

    @patch("backend.core.app.settings")
    def test_validates_database_url(self, mock_settings):
        """Should validate database URL format."""
        mock_settings.database_url = "mysql://localhost/db"  # Wrong protocol
        mock_settings.redis_url = "redis://localhost:6379"
        mock_settings.session_cookie_max_age = 30 * 24 * 60 * 60
        mock_settings.csrf_token_length = 32
        mock_settings.max_concurrent_feeds = 10
        mock_settings.request_timeout = 30
        mock_settings.log_level = "info"

        valid, errors = validate_configuration()

        assert valid is False
        assert any("PostgreSQL" in e or "DATABASE_URL" in e for e in errors)

    @patch("backend.core.app.settings")
    def test_validates_redis_url(self, mock_settings):
        """Should validate Redis URL is set."""
        mock_settings.database_url = "postgresql://localhost/db"
        mock_settings.redis_url = ""  # Empty
        mock_settings.session_cookie_max_age = 30 * 24 * 60 * 60
        mock_settings.csrf_token_length = 32
        mock_settings.max_concurrent_feeds = 10
        mock_settings.request_timeout = 30
        mock_settings.log_level = "info"

        valid, errors = validate_configuration()

        assert valid is False
        assert any("REDIS_URL" in e for e in errors)

    @patch("backend.core.app.settings")
    def test_validates_session_cookie_max_age(self, mock_settings):
        """Should validate session max age is positive."""
        mock_settings.database_url = "postgresql://localhost/db"
        mock_settings.redis_url = "redis://localhost:6379"
        mock_settings.session_cookie_max_age = -1  # Invalid
        mock_settings.csrf_token_length = 32
        mock_settings.max_concurrent_feeds = 10
        mock_settings.request_timeout = 30
        mock_settings.log_level = "info"

        valid, errors = validate_configuration()

        assert valid is False
        assert any("SESSION_COOKIE_MAX_AGE" in e for e in errors)

    @patch("backend.core.app.settings")
    def test_warns_on_short_csrf_token(self, mock_settings):
        """Should warn on short CSRF token length."""
        mock_settings.database_url = "postgresql://localhost/db"
        mock_settings.redis_url = "redis://localhost:6379"
        mock_settings.session_cookie_max_age = 30 * 24 * 60 * 60
        mock_settings.csrf_token_length = 8  # Too short
        mock_settings.max_concurrent_feeds = 10
        mock_settings.request_timeout = 30
        mock_settings.log_level = "info"

        valid, errors = validate_configuration()

        # Should still be valid, but warning logged
        assert valid is True
        assert errors == []

    @patch("backend.core.app.settings")
    def test_validates_max_concurrent_feeds_positive(self, mock_settings):
        """Should validate max concurrent feeds is positive."""
        mock_settings.database_url = "postgresql://localhost/db"
        mock_settings.redis_url = "redis://localhost:6379"
        mock_settings.session_cookie_max_age = 30 * 24 * 60 * 60
        mock_settings.csrf_token_length = 32
        mock_settings.max_concurrent_feeds = 0  # Invalid
        mock_settings.request_timeout = 30
        mock_settings.log_level = "info"

        valid, errors = validate_configuration()

        assert valid is False
        assert any("MAX_CONCURRENT_FEEDS" in e for e in errors)

    @patch("backend.core.app.settings")
    def test_warns_on_high_concurrent_feeds(self, mock_settings):
        """Should warn on very high concurrent feeds."""
        mock_settings.database_url = "postgresql://localhost/db"
        mock_settings.redis_url = "redis://localhost:6379"
        mock_settings.session_cookie_max_age = 30 * 24 * 60 * 60
        mock_settings.csrf_token_length = 32
        mock_settings.max_concurrent_feeds = 150  # High
        mock_settings.request_timeout = 30
        mock_settings.log_level = "info"

        valid, errors = validate_configuration()

        # Should be valid with warning
        assert valid is True
        assert errors == []

    @patch("backend.core.app.settings")
    def test_validates_request_timeout_positive(self, mock_settings):
        """Should validate request timeout is positive."""
        mock_settings.database_url = "postgresql://localhost/db"
        mock_settings.redis_url = "redis://localhost:6379"
        mock_settings.session_cookie_max_age = 30 * 24 * 60 * 60
        mock_settings.csrf_token_length = 32
        mock_settings.max_concurrent_feeds = 10
        mock_settings.request_timeout = -5  # Invalid
        mock_settings.log_level = "info"

        valid, errors = validate_configuration()

        assert valid is False
        assert any("REQUEST_TIMEOUT" in e for e in errors)

    @patch("backend.core.app.settings")
    def test_validates_log_level_valid(self, mock_settings):
        """Should validate log level is one of allowed values."""
        mock_settings.database_url = "postgresql://localhost/db"
        mock_settings.redis_url = "redis://localhost:6379"
        mock_settings.session_cookie_max_age = 30 * 24 * 60 * 60
        mock_settings.csrf_token_length = 32
        mock_settings.max_concurrent_feeds = 10
        mock_settings.request_timeout = 30
        mock_settings.log_level = "invalid"  # Invalid level

        valid, errors = validate_configuration()

        assert valid is False
        assert any("LOG_LEVEL" in e for e in errors)

    @patch("backend.core.app.settings")
    def test_returns_success_for_valid_config(self, mock_settings):
        """Should return success for valid configuration."""
        mock_settings.database_url = "postgresql://localhost/db"
        mock_settings.redis_url = "redis://localhost:6379"
        mock_settings.session_cookie_max_age = 30 * 24 * 60 * 60
        mock_settings.csrf_token_length = 32
        mock_settings.max_concurrent_feeds = 10
        mock_settings.request_timeout = 30
        mock_settings.log_level = "info"

        valid, errors = validate_configuration()

        assert valid is True
        assert errors == []

    @patch("backend.core.app.settings")
    def test_handles_exception_during_validation(self, mock_settings):
        """Should handle exceptions during validation."""
        mock_settings.database_url = MagicMock(
            side_effect=Exception("Test error")
        )

        valid, errors = validate_configuration()

        assert valid is False
        assert len(errors) > 0


class TestGetConfigurationHelp:
    """Test configuration help."""

    def test_returns_help_for_database_url(self):
        """Should return help text for DATABASE_URL."""
        help = get_configuration_help()
        assert "DATABASE_URL" in help
        assert "postgresql://" in help["DATABASE_URL"]

    def test_returns_help_for_redis_url(self):
        """Should return help text for REDIS_URL."""
        help = get_configuration_help()
        assert "REDIS_URL" in help
        assert "redis://" in help["REDIS_URL"]

    def test_returns_help_for_session_timeout(self):
        """Should return help text for SESSION_TIMEOUT_DAYS."""
        help = get_configuration_help()
        assert "SESSION_TIMEOUT_DAYS" in help

    def test_returns_help_for_cookie_secure(self):
        """Should return help text for COOKIE_SECURE."""
        help = get_configuration_help()
        assert "COOKIE_SECURE" in help
        assert "HTTPS" in help["COOKIE_SECURE"]

    def test_returns_help_for_environment(self):
        """Should return help text for ENVIRONMENT."""
        help = get_configuration_help()
        assert "ENVIRONMENT" in help

    def test_returns_help_for_log_level(self):
        """Should return help text for LOG_LEVEL."""
        help = get_configuration_help()
        assert "LOG_LEVEL" in help
        assert "debug, info, warning, error, critical" in help["LOG_LEVEL"]

    def test_returns_help_for_max_concurrent_feeds(self):
        """Should return help text for MAX_CONCURRENT_FEEDS."""
        help = get_configuration_help()
        assert "MAX_CONCURRENT_FEEDS" in help
