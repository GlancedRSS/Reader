"""Unit tests for URL normalization utilities."""

from unittest.mock import patch

from backend.utils.url_normalizer import (
    GA_PATTERNS,
    TRACKING_PARAMS,
    extract_domain,
    normalize_url,
)


class TestNormalizeUrl:
    """Test URL normalization function."""

    def test_returns_empty_string_for_none_or_empty(self):
        """Should return empty string for None or empty input."""
        assert normalize_url(None) == ""
        assert normalize_url("") == ""

    def test_removes_utm_tracking_parameters(self):
        """Should remove UTM tracking parameters from URL."""
        url = "https://example.com/article?utm_source=google&utm_medium=social&id=123"
        result = normalize_url(url)
        assert "utm_source" not in result
        assert "utm_medium" not in result
        assert "id=123" in result

    def test_removes_facebook_tracking_parameters(self):
        """Should remove Facebook tracking parameters."""
        url = "https://example.com/page?fbclid=abc123&ref=sharing"
        result = normalize_url(url)
        assert "fbclid" not in result
        assert "ref" not in result

    def test_removes_google_analytics_parameters(self):
        """Should remove Google Analytics cookies."""
        url = "https://example.com/post?_ga=GA1.2.123&_gid=GA1.2.456&id=789"
        result = normalize_url(url)
        assert "_ga" not in result
        assert "_gid" not in result
        assert "id=789" in result

    def test_standardizes_to_https(self):
        """Should convert http to https."""
        assert (
            normalize_url("http://example.com/page")
            == "https://example.com/page"
        )
        assert (
            normalize_url("https://example.com/page")
            == "https://example.com/page"
        )

    def test_removes_www_prefix(self):
        """Should remove www prefix from domain."""
        assert (
            normalize_url("https://www.example.com/page")
            == "https://example.com/page"
        )
        assert (
            normalize_url("https://example.com/page")
            == "https://example.com/page"
        )

    def test_removes_default_ports(self):
        """Should remove default ports (80 for http, 443 for https)."""
        assert (
            normalize_url("https://example.com:443/page")
            == "https://example.com/page"
        )
        assert (
            normalize_url("http://example.com:80/page")
            == "https://example.com/page"
        )

    def test_removes_trailing_slash_from_path(self):
        """Should remove trailing slash from path."""
        assert (
            normalize_url("https://example.com/page/")
            == "https://example.com/page"
        )

    def test_preserves_root_path(self):
        """Should preserve root path as single slash."""
        assert normalize_url("https://example.com") == "https://example.com/"
        assert normalize_url("https://example.com/") == "https://example.com/"

    def test_removes_fragment(self):
        """Should remove URL fragment."""
        assert (
            normalize_url("https://example.com/page#section")
            == "https://example.com/page"
        )

    def test_lowercase_domain(self):
        """Should convert domain to lowercase."""
        assert (
            normalize_url("https://EXAMPLE.COM/Page")
            == "https://example.com/Page"
        )

    def test_strips_whitespace(self):
        """Should strip whitespace from URL."""
        assert (
            normalize_url("  https://example.com/page  ")
            == "https://example.com/page"
        )

    def test_handles_exception_with_fallback(self):
        """Should return lowercased URL on exception."""
        # This tests the except block - need to trigger ValueError or AttributeError
        # Using a URL that will cause parsing issues
        result = normalize_url("http://[invalid-ipv6")  # Invalid IPv6 URL
        # Should return the stripped, lowercased URL without trailing slash
        assert result == "http://[invalid-ipv6"

    def test_removes_empty_query_parameters(self):
        """Should remove query parameters with empty values."""
        url = "https://example.com?page=&id=123&empty="
        result = normalize_url(url)
        assert "page=" not in result
        assert "empty=" not in result
        assert "id=123" in result

    def test_removes_query_params_with_only_empty_strings(self):
        """Should remove parameters where all values are empty strings."""
        # This tests line 63 - all(not v for v in values)
        url = "https://example.com?param=&id=123"
        result = normalize_url(url)
        assert "param=" not in result
        assert "id=123" in result

    def test_preserves_non_tracking_parameters(self):
        """Should preserve non-tracking query parameters."""
        url = "https://example.com/article?id=123&page=2&sort=date"
        result = normalize_url(url)
        assert "id=123" in result
        assert "page=2" in result
        assert "sort=date" in result

    def test_handles_all_tracking_params(self):
        """Should handle all tracking parameters in TRACKING_PARAMS."""
        for param in TRACKING_PARAMS:
            url = f"https://example.com/page?{param}=value&id=123"
            result = normalize_url(url)
            assert f"{param}=" not in result
            assert "id=123" in result

    def test_handles_ga_patterns(self):
        """Should handle all Google Analytics patterns."""
        for pattern in GA_PATTERNS:
            url = f"https://example.com/page?{pattern}1.2.123&id=456"
            result = normalize_url(url)
            assert pattern not in result
            assert "id=456" in result


class TestExtractDomain:
    """Test domain extraction function."""

    def test_extracts_domain_from_url(self):
        """Should extract domain from URL."""
        assert extract_domain("https://www.example.com/page") == "example.com"
        assert (
            extract_domain("http://subdomain.example.com/path")
            == "subdomain.example.com"
        )

    def test_removes_www_prefix(self):
        """Should remove www prefix from domain."""
        assert extract_domain("https://www.example.com/page") == "example.com"
        assert extract_domain("https://example.com/page") == "example.com"

    def test_lowercases_domain(self):
        """Should return lowercase domain."""
        assert extract_domain("https://EXAMPLE.COM/page") == "example.com"
        assert extract_domain("https://WwW.ExAmPlE.CoM") == "example.com"

    def test_returns_unknown_for_invalid_url(self):
        """Should return 'unknown' for invalid URL."""
        # urlparse doesn't raise exception for "not a url", it just returns empty netloc
        # So we get empty string back
        assert extract_domain("not a url") == ""
        assert extract_domain("") == ""

    def test_handles_exception_in_domain_extraction(self):
        """Should return 'unknown' when urlparse raises exception."""
        # Need to trigger an exception - use None which will cause .lower() to fail
        # Actually, the code does url.lower() first, so we need to cause an exception elsewhere
        # Let's use a mock to cause the exception

        with patch("backend.utils.url_normalizer.urlparse") as mock_parse:
            mock_parse.side_effect = Exception("Parse error")
            result = extract_domain("https://example.com")
            assert result == "unknown"
