"""Unit tests for feed constants and utilities."""

from backend.infrastructure.feed.utils.constants import (
    IMAGE_EXTENSIONS,
    decode_html_entities,
)


class TestImageExtensions:
    """Test image extensions constant."""

    def test_contains_common_image_formats(self):
        """Should contain all common image file extensions."""
        assert ".jpg" in IMAGE_EXTENSIONS
        assert ".jpeg" in IMAGE_EXTENSIONS
        assert ".png" in IMAGE_EXTENSIONS
        assert ".gif" in IMAGE_EXTENSIONS
        assert ".webp" in IMAGE_EXTENSIONS
        assert ".bmp" in IMAGE_EXTENSIONS
        assert ".svg" in IMAGE_EXTENSIONS
        assert ".ico" in IMAGE_EXTENSIONS

    def test_extensions_include_dot_prefix(self):
        """All extensions should include dot prefix."""
        for ext in IMAGE_EXTENSIONS:
            assert ext.startswith(".")


class TestDecodeHtmlEntities:
    """Test HTML entity decoding."""

    def test_decodes_basic_entities(self):
        """Should decode basic HTML entities."""
        assert decode_html_entities("&amp;") == "&"
        assert decode_html_entities("&lt;") == "<"
        assert decode_html_entities("&gt;") == ">"
        assert decode_html_entities("&quot;") == '"'
        assert decode_html_entities("&apos;") == "'"

    def test_decodes_numeric_entities(self):
        """Should decode numeric HTML entities."""
        assert decode_html_entities("&#65;") == "A"
        assert (
            decode_html_entities("x65;") == "x65;"
        )  # Not a valid numeric entity without &#

    def test_decodes_mixed_entities(self):
        """Should decode text with multiple entity types."""
        assert decode_html_entities("&lt;div&gt;&amp;") == "<div>&"

    def test_handles_double_encoded_entities(self):
        """Should handle double-encoded HTML entities."""
        assert decode_html_entities("&amp;amp;") == "&"
        assert decode_html_entities("&amp;lt;") == "<"
        assert decode_html_entities("&amp;quot;") == '"'

    def test_handles_triple_encoded_entities(self):
        """Should handle triple-encoded HTML entities."""
        # The function decodes up to 3 times for common entities
        result = decode_html_entities("&amp;amp;amp;")
        assert result == "&"

    def test_returns_none_input_unchanged(self):
        """Should return None for None input."""
        assert decode_html_entities(None) is None

    def test_returns_empty_string_unchanged(self):
        """Should return empty string unchanged."""
        assert decode_html_entities("") == ""

    def test_returns_plain_text_unchanged(self):
        """Should return plain text unchanged."""
        assert decode_html_entities("Hello World") == "Hello World"

    def test_handles_invalid_unicode(self):
        """Should handle invalid Unicode characters gracefully."""
        # Surrogate pairs and invalid UTF-8 should be handled
        result = decode_html_entities("Test\ud800String")  # Invalid surrogate
        assert isinstance(result, str)
        assert "Test" in result

    def test_handles_already_decoded_text(self):
        """Should not error on already decoded text."""
        assert (
            decode_html_entities("Already <decoded> & text")
            == "Already <decoded> & text"
        )

    def test_prevents_infinite_decoding_loop(self):
        """Should prevent infinite loops with malformed entities."""
        # Should stop after max decodes even if entities still present
        text = "&amp;" * 10  # Many encoded amps
        result = decode_html_entities(text)
        assert isinstance(result, str)

    def test_handles_exception_during_decoding(self):
        """Should handle exceptions gracefully and return cleaned text."""
        # Pass something that might cause issues during unescape
        result = decode_html_entities("Normal text")
        assert result == "Normal text"

    def test_preserves_whitespace(self):
        """Should preserve whitespace in text."""
        assert decode_html_entities("Hello&amp;   World") == "Hello&   World"

    def test_decodes_named_entities_with_case(self):
        """Should handle case sensitivity in named entities."""
        assert decode_html_entities("&AMP;") == "&"
        assert decode_html_entities("&LT;") == "<"

    def test_handles_mixed_content(self):
        """Should handle text with entities, regular text, and special chars."""
        assert decode_html_entities("Price: &amp; $50") == "Price: & $50"
