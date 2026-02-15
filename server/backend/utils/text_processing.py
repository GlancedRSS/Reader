"""Text processing utilities for content analysis."""

import re


def calculate_reading_time(text: str | None, wpm: int = 200) -> int | None:
    """Calculate estimated reading time in minutes based on word count."""
    if not text or not text.strip():
        return None

    cleaned_text = re.sub(r"\s+", " ", text.strip())

    word_count = len(cleaned_text.split())

    return max(1, round(word_count / wpm))
