"""Shared constants and utility functions for feed infrastructure."""

import html

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".bmp",
    ".svg",
    ".ico",
}


def decode_html_entities(text: str) -> str:
    """Decode HTML entities in text content with double-encoding fix.

    Handles nested encoding and invalid Unicode characters.

    Args:
        text: Text potentially containing HTML entities.

    Returns:
        Decoded text with entities resolved and surrogates handled.

    """
    if not text:
        return text

    try:
        text = html.unescape(text)

        previous_text = ""
        max_decodes = 3

        while (
            (
                "&amp;" in text
                or "&lt;" in text
                or "&gt;" in text
                or "&quot;" in text
            )
            and previous_text != text
            and max_decodes > 0
        ):
            previous_text = text
            text = html.unescape(text)
            max_decodes -= 1

        return text.encode("utf-8", errors="replace").decode("utf-8")

    except Exception:
        return text.encode("utf-8", errors="replace").decode("utf-8")
