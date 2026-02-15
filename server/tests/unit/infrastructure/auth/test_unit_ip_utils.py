"""Unit tests for IP utilities."""

from unittest.mock import MagicMock, patch

import pytest

from backend.infrastructure.auth.ip_utils import IPUtils


class TestValidateIp:
    """Test IP address validation."""

    def test_validates_ipv4_address(self):
        """Should validate and normalize IPv4 addresses."""
        assert IPUtils._validate_ip("192.168.1.1") == "192.168.1.1"
        assert IPUtils._validate_ip("  127.0.0.1  ") == "127.0.0.1"

    def test_validates_ipv6_address(self):
        """Should validate and normalize IPv6 addresses."""
        assert IPUtils._validate_ip("::1") == "::1"
        assert IPUtils._validate_ip("2001:db8::1") == "2001:db8::1"

    def test_returns_none_for_invalid_ip(self):
        """Should return None for invalid IP strings."""
        assert IPUtils._validate_ip("not-an-ip") is None
        assert IPUtils._validate_ip("") is None
        assert IPUtils._validate_ip("999.999.999.999") is None

    def test_raises_error_for_none_input(self):
        """Should raise error for None input."""
        # The implementation calls .strip() which fails on None
        with pytest.raises(AttributeError):
            IPUtils._validate_ip(None)


class TestGetClientIp:
    """Test client IP extraction from requests."""

    def test_returns_direct_ip_when_no_headers(self):
        """Should return direct connection IP when no proxy headers."""
        request = MagicMock()
        request.client.host = "192.168.1.100"
        request.headers.get = MagicMock(return_value=None)

        with patch(
            "backend.infrastructure.auth.ip_utils.settings"
        ) as mock_settings:
            mock_settings.trusted_proxies = None

            result = IPUtils.get_client_ip(request)
            assert result == "192.168.1.100"

    def test_returns_direct_ip_when_not_from_trusted_proxy(self):
        """Should ignore proxy headers when not from trusted proxy."""
        request = MagicMock()
        request.client.host = "8.8.8.8"  # Not in trusted range
        request.headers.get = MagicMock(return_value="192.168.1.100")

        with patch(
            "backend.infrastructure.auth.ip_utils.settings"
        ) as mock_settings:
            mock_settings.trusted_proxies = ["10.0.0.0/8"]

            result = IPUtils.get_client_ip(request)
            assert result == "8.8.8.8"

    def test_trusts_x_forwarded_for_from_trusted_proxy(self):
        """Should trust X-Forwarded-For from trusted proxy."""
        request = MagicMock()
        request.client.host = "10.0.0.1"  # In trusted range
        request.headers.get = MagicMock(
            side_effect=lambda k, d=None: {
                "x-forwarded-for": "8.8.8.8, 10.0.0.2",  # 8.8.8.8 is Google DNS (public)
                "x-real-ip": None,
            }.get(k, d)
        )

        with patch(
            "backend.infrastructure.auth.ip_utils.settings"
        ) as mock_settings:
            mock_settings.trusted_proxies = ["10.0.0.0/8"]

            result = IPUtils.get_client_ip(request)
            assert result == "8.8.8.8"

    def test_trusts_x_real_ip_from_trusted_proxy(self):
        """Should trust X-Real-IP from trusted proxy."""
        request = MagicMock()
        request.client.host = "10.0.0.1"
        request.headers.get = MagicMock(
            side_effect=lambda k, d=None: {
                "x-forwarded-for": None,
                "x-real-ip": "1.1.1.1",  # Cloudflare DNS (public)
            }.get(k, d)
        )

        with patch(
            "backend.infrastructure.auth.ip_utils.settings"
        ) as mock_settings:
            mock_settings.trusted_proxies = ["10.0.0.0/8"]

            result = IPUtils.get_client_ip(request)
            assert result == "1.1.1.1"

    def test_skips_private_ips_in_forwarded_for(self):
        """Should skip private IPs when parsing X-Forwarded-For."""
        request = MagicMock()
        request.client.host = "10.0.0.1"
        request.headers.get = MagicMock(
            side_effect=lambda k, d=None: {
                "x-forwarded-for": "192.168.1.50, 1.1.1.1",  # 1.1.1.1 is Cloudflare DNS (public)
                "x-real-ip": None,
            }.get(k, d)
        )

        with patch(
            "backend.infrastructure.auth.ip_utils.settings"
        ) as mock_settings:
            mock_settings.trusted_proxies = ["10.0.0.0/8"]

            result = IPUtils.get_client_ip(request)
            assert result == "1.1.1.1"

    def test_falls_back_to_direct_ip_when_no_public_ip_in_forwarded_for(self):
        """Should fall back to direct IP when all forwarded IPs are private."""
        request = MagicMock()
        request.client.host = "10.0.0.1"
        request.headers.get = MagicMock(
            side_effect=lambda k, d=None: {
                "x-forwarded-for": "192.168.1.50, 172.16.0.50",
                "x-real-ip": None,
            }.get(k, d)
        )

        with patch(
            "backend.infrastructure.auth.ip_utils.settings"
        ) as mock_settings:
            mock_settings.trusted_proxies = ["10.0.0.0/8"]

            result = IPUtils.get_client_ip(request)
            assert result == "10.0.0.1"

    def test_returns_zero_fallback_when_no_valid_ip(self):
        """Should return 0.0.0.0 when no valid IP can be determined."""
        request = MagicMock()
        request.client = None
        request.headers.get = MagicMock(return_value=None)

        with patch(
            "backend.infrastructure.auth.ip_utils.settings"
        ) as mock_settings:
            mock_settings.trusted_proxies = None

            result = IPUtils.get_client_ip(request)
            assert result == "0.0.0.0"

    def test_handles_cidr_trusted_proxy_ranges(self):
        """Should handle CIDR notation for trusted proxy ranges."""
        request = MagicMock()
        request.client.host = "172.31.0.1"  # In 172.16.0.0/12 range
        request.headers.get = MagicMock(
            side_effect=lambda k, d=None: {
                "x-forwarded-for": "8.8.8.8",  # Google DNS (public)
                "x-real-ip": None,
            }.get(k, d)
        )

        with patch(
            "backend.infrastructure.auth.ip_utils.settings"
        ) as mock_settings:
            mock_settings.trusted_proxies = ["172.16.0.0/12"]

            result = IPUtils.get_client_ip(request)
            assert result == "8.8.8.8"

    def test_handles_exact_match_trusted_proxy(self):
        """Should handle exact IP match for trusted proxy."""
        request = MagicMock()
        request.client.host = "192.168.1.1"
        request.headers.get = MagicMock(
            side_effect=lambda k, d=None: {
                "x-forwarded-for": "8.8.4.4",  # Google DNS (public)
                "x-real-ip": None,
            }.get(k, d)
        )

        with patch(
            "backend.infrastructure.auth.ip_utils.settings"
        ) as mock_settings:
            mock_settings.trusted_proxies = ["192.168.1.1"]

            result = IPUtils.get_client_ip(request)
            assert result == "8.8.4.4"

    def test_returns_zero_fallback_for_invalid_direct_ip(self):
        """Should return fallback when direct IP is invalid."""
        request = MagicMock()
        request.client.host = "not-an-ip"
        request.headers.get = MagicMock(return_value=None)

        with patch(
            "backend.infrastructure.auth.ip_utils.settings"
        ) as mock_settings:
            mock_settings.trusted_proxies = None

            result = IPUtils.get_client_ip(request)
            assert result == "0.0.0.0"

    def test_handles_empty_trusted_proxies_list(self):
        """Should handle empty trusted proxies list."""
        request = MagicMock()
        request.client.host = "8.8.8.8"  # Public IP
        request.headers.get = MagicMock(
            side_effect=lambda k, d=None: {
                "x-forwarded-for": "192.168.1.100",
                "x-real-ip": None,
            }.get(k, d)
        )

        with patch(
            "backend.infrastructure.auth.ip_utils.settings"
        ) as mock_settings:
            mock_settings.trusted_proxies = []

            result = IPUtils.get_client_ip(request)
            # Should not trust headers since no trusted proxies configured
            assert result == "8.8.8.8"
