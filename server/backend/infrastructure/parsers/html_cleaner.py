"""HTML cleaning and sanitization utilities for RSS feed content."""

import re
from html import unescape

import bleach
from bs4 import BeautifulSoup


def decode_html_entities(text: str) -> str:
    """Decode HTML entities in text."""
    return unescape(text)


class HTMLCleaner:
    """Cleans and sanitizes HTML content while preserving safe structure."""

    TRUSTED_IFRAME_DOMAINS = {
        "youtube.com",
        "www.youtube.com",
        "youtu.be",
        "vimeo.com",
        "player.vimeo.com",
        "open.spotify.com",
        "embed.music.apple.com",
        "soundcloud.com",
        "w.soundcloud.com",
    }

    def __init__(self) -> None:
        """Initialize the HTML cleaner with allowed tags and attributes."""
        self.allowed_tags = {
            "p",
            "br",
            "div",
            "span",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "ul",
            "ol",
            "li",
            "dl",
            "dt",
            "dd",
            "strong",
            "b",
            "em",
            "i",
            "u",
            "s",
            "sub",
            "sup",
            "blockquote",
            "pre",
            "code",
            "a",
            "img",
            "video",
            "audio",
            "source",
            "svg",
            "track",
            "table",
            "thead",
            "tbody",
            "tr",
            "th",
            "td",
            "article",
            "section",
            "nav",
            "aside",
            "header",
            "footer",
            "main",
            "figure",
            "figcaption",
            "details",
            "summary",
            "time",
            "mark",
            "cite",
            "q",
            "abbr",
            "address",
            "hr",
            "small",
            "iframe",
        }

        self.allowed_attributes = {
            "*": ["class", "title"],
            "a": ["href", "title"],
            "img": [
                "src",
                "alt",
                "title",
                "width",
                "height",
                "loading",
            ],
            "video": [
                "src",
                "poster",
                "width",
                "height",
                "controls",
                "autoplay",
                "loop",
                "muted",
            ],
            "audio": ["src", "controls", "autoplay", "loop", "muted"],
            "source": ["src", "type", "media"],
            "track": ["src", "kind", "srclang", "label", "default"],
            "svg": ["width", "height", "viewBox", "xmlns"],
            "blockquote": ["cite"],
            "code": ["class"],
            "pre": ["class"],
            "td": ["colspan", "rowspan"],
            "th": ["colspan", "rowspan", "scope"],
            "time": ["datetime"],
            "figure": ["class"],
            "figcaption": ["class"],
            "iframe": [
                "src",
                "width",
                "height",
                "allowfullscreen",
                "allow",
                "frameborder",
                "scrolling",
                "referrerpolicy",
                "loading",
            ],
        }

        self.cleaner = bleach.Cleaner(
            tags=self.allowed_tags,
            attributes=self.allowed_attributes,
            strip=True,
            strip_comments=True,
            css_sanitizer=None,
        )

    def _is_trusted_iframe_domain(self, src: str) -> bool:
        """Check if iframe src URL is from a trusted domain."""
        if not src or not isinstance(src, str):
            return False

        try:
            from urllib.parse import urlparse

            parsed = urlparse(src)
            domain = parsed.netloc.lower()

            for trusted in self.TRUSTED_IFRAME_DOMAINS:
                if domain == trusted or domain.endswith(f".{trusted}"):
                    return True

            return False
        except Exception:
            return False

    def clean_html(self, html_content: str) -> str:
        """Clean HTML content while preserving safe structure and formatting."""
        if not html_content:
            return ""

        pre_blocks: list[str] = []

        def extract_pre(match: re.Match[str]) -> str:
            pre_blocks.append(match.group(0))
            return f"__PRE_PLACEHOLDER_{len(pre_blocks) - 1}__"

        protected_html = re.sub(
            r"<pre[^>]*>.*?</pre>", extract_pre, html_content, flags=re.DOTALL
        )

        try:
            soup = BeautifulSoup(protected_html, "html.parser")

            dangerous_tags = [
                "script",
                "style",
                "noscript",
                "object",
                "embed",
                "form",
                "input",
                "button",
            ]
            for tag in soup(dangerous_tags):
                tag.decompose()

            for iframe in soup.find_all("iframe"):
                src = iframe.get("src", "")
                if isinstance(src, str) and not self._is_trusted_iframe_domain(
                    src
                ):
                    iframe.decompose()

            pre_cleaned_html = str(soup)
            sanitized_html = self.cleaner.clean(pre_cleaned_html)

            sanitized_html = re.sub(
                r'style\s*=\s*["\'][^"\']*(javascript|expression|behavior|@import)[^"\']*["\']',
                "",
                sanitized_html,
                flags=re.IGNORECASE,
            )

            sanitized_html = re.sub(
                r'(href|src)\s*=\s*["\']\s*(javascript|data|vbscript):[^"\']*["\']',
                r'\1=""',
                sanitized_html,
                flags=re.IGNORECASE,
            )

            for i, block in enumerate(pre_blocks):
                sanitized_html = sanitized_html.replace(
                    f"__PRE_PLACEHOLDER_{i}__", block
                )

            # Now extract pre blocks again to protect them from whitespace normalization
            pre_blocks_final: list[str] = []

            def extract_pre_final(match: re.Match[str]) -> str:
                pre_blocks_final.append(match.group(0))
                return f"__PRE_FINAL_{len(pre_blocks_final) - 1}__"

            sanitized_html = re.sub(
                r"<pre[^>]*>.*?</pre>",
                extract_pre_final,
                sanitized_html,
                flags=re.DOTALL,
            )

            sanitized_html = decode_html_entities(sanitized_html)

            inline_tags = [
                "a",
                "strong",
                "b",
                "em",
                "i",
                "u",
                "s",
                "sub",
                "sup",
                "code",
                "mark",
                "cite",
                "q",
                "abbr",
                "time",
                "small",
            ]
            for tag_name in inline_tags:
                sanitized_html = re.sub(
                    rf"(<{tag_name}\b[^>]*>)", r" \1 ", sanitized_html
                )
                sanitized_html = re.sub(
                    rf"(</{tag_name}>)", r" \1 ", sanitized_html
                )

            # Normalize whitespace, but preserve pre tag placeholders
            sanitized_html = re.sub(r"\s+", " ", sanitized_html)

            # Restore pre tag content with original formatting
            for i, block in enumerate(pre_blocks_final):
                sanitized_html = sanitized_html.replace(
                    f"__PRE_FINAL_{i}__", block
                )

            return sanitized_html.strip()

        except Exception as e:
            import structlog

            logger = structlog.get_logger()
            logger.warning("Error sanitizing HTML", error=str(e))
            text = re.sub(r"<[^>]+>", " ", html_content)
            text = decode_html_entities(text)
            return re.sub(r"\s+", " ", text).strip()

    def html_to_text(self, html_content: str) -> str:
        """Clean HTML content to plain text for search indexing."""
        if not html_content:
            return ""

        try:
            soup = BeautifulSoup(html_content, "html.parser")

            for tag in soup(
                ["script", "style", "noscript", "iframe", "object", "embed"]
            ):
                tag.decompose()

            text = soup.get_text(separator=" ", strip=True)
            text = decode_html_entities(text)
            text = re.sub(r"\s+", " ", text)
            return text.strip()

        except Exception as e:
            import structlog

            logger = structlog.get_logger()
            logger.warning("Error cleaning HTML to text", error=str(e))
            text = re.sub(r"<[^>]+>", " ", html_content)
            text = decode_html_entities(text)
            return re.sub(r"\s+", " ", text).strip()

    def clean_html_content(self, html_content: str) -> tuple[str, str | None]:
        """Clean HTML content and extract first image."""
        if not html_content or not html_content.strip():
            return "", None

        clean_text = self.clean_html(html_content)

        try:
            soup = BeautifulSoup(html_content, "html.parser")
            img_tag = soup.find("img")
            image_url = None
            if img_tag:
                src = img_tag.get("src")
                if src and isinstance(src, str):
                    image_url = src
        except Exception:
            image_url = None

        return clean_text, image_url
