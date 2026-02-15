"""URL normalization for article deduplication."""

from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
    "msclkid",
    "twclid",
    "igshid",
    "mc_eid",
    "ref",
    "referrer",
    "source",
    "campaign",
    "medium",
    "ncid",
    "cid",
}

GA_PATTERNS = ("_ga", "_gid")


def normalize_url(url: str) -> str:
    """Normalize URL by removing tracking params and standardizing format."""
    if not url:
        return ""

    try:
        parsed = urlparse(url.strip())
        original_scheme = parsed.scheme
        scheme = "https"

        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]

        if (original_scheme == "https" and netloc.endswith(":443")) or (
            original_scheme == "http" and netloc.endswith(":80")
        ):
            netloc = netloc.rsplit(":", 1)[0]

        query_params: dict[str, list[str]] = parse_qs(parsed.query)
        clean_params: dict[str, list[str]] = {}

        for key, values in query_params.items():
            key_lower = key.lower()

            if key_lower in TRACKING_PARAMS:
                continue

            if any(
                key_lower.startswith(ga_pattern) for ga_pattern in GA_PATTERNS
            ):
                continue

            if not values or all(not v for v in values):
                continue

            clean_params[key] = values

        query = urlencode(clean_params, doseq=True) if clean_params else ""
        path = parsed.path.rstrip("/") or "/"
        fragment = ""

        return urlunparse(
            (scheme, netloc, path, parsed.params, query, fragment)
        )

    except (ValueError, AttributeError):
        return url.strip().lower().rstrip("/")


def extract_domain(url: str) -> str:
    """Extract domain from URL, removing www prefix."""
    try:
        parsed = urlparse(url.lower())
        domain = parsed.netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return "unknown"
