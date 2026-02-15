"""Utility functions for IP address extraction."""

import ipaddress
from typing import Any

import structlog

from backend.core.app import settings

logger = structlog.get_logger()


class IPUtils:
    """Utility functions for IP address extraction."""

    @staticmethod
    def _validate_ip(ip_str: str) -> str | None:
        """Validate and normalize an IP address.

        Args:
            ip_str: The IP string to validate.

        Returns:
            The normalized IP address, or None if invalid.

        """
        try:
            ip = ipaddress.ip_address(ip_str.strip())
            return str(ip)
        except ValueError:
            return None

    @staticmethod
    def get_client_ip(request: Any) -> str:
        """Get the real client IP address, checking for proxy headers.

        Only trusts proxy headers if the request comes from a configured
        trusted proxy. Otherwise falls back to the direct connection IP.

        Args:
            request: The HTTP request object.

        Returns:
            The validated client IP address.

        """
        direct_ip = request.client.host if request.client else None
        trusted_proxies = getattr(settings, "trusted_proxies", None)

        proxy_is_trusted = False
        if trusted_proxies and direct_ip:
            for trusted in trusted_proxies:
                try:
                    network = ipaddress.ip_network(trusted, strict=False)
                    if ipaddress.ip_address(direct_ip) in network:
                        proxy_is_trusted = True
                        break
                except ValueError:
                    if direct_ip == trusted:
                        proxy_is_trusted = True
                        break

        if proxy_is_trusted:
            forwarded_for = request.headers.get("x-forwarded-for")
            if forwarded_for:
                for ip_segment in forwarded_for.split(","):
                    validated = IPUtils._validate_ip(ip_segment)
                    if validated:
                        try:
                            ip_obj = ipaddress.ip_address(validated)
                            if not ip_obj.is_private:
                                return validated
                        except ValueError:
                            pass

            real_ip = request.headers.get("x-real-ip")
            if real_ip:
                validated = IPUtils._validate_ip(real_ip)
                if validated:
                    return validated

        if direct_ip:
            validated = IPUtils._validate_ip(direct_ip)
            if validated:
                return validated

        logger.warning("Could not determine client IP address, using fallback")
        return "0.0.0.0"
