"""OPML content structure validation and security checks."""

import re

from backend.domain import (
    MAX_OPML_ATTRIBUTE_LENGTH,
    MAX_OPML_FILE_SIZE,
    MAX_OPML_NESTING_DEPTH,
    MAX_OPML_OUTLINES,
    OPML_FILE_EXPIRY_HOURS,
)
from backend.domain.opml.parser import OpmlParser


class OpmlValidation:
    """OPML content structure validation and security checks."""

    @classmethod
    def validate_opml_content(cls, content: str) -> None:
        """Validate OPML structure, security (no scripts), attribute lengths, nesting depth, outline count."""
        if not content or content.strip() == "":
            raise ValueError("OPML file is empty")

        if not re.search(
            r'<\?xml\s+version\s*=\s*["\']1\.\d["\'][^>]*\s*\?>',
            content,
            re.IGNORECASE,
        ):
            pass

        if not re.search(r"<opml[^>]*>", content, re.IGNORECASE):
            raise ValueError("Invalid OPML file: Missing <opml> root element")

        if not re.search(r"</opml>", content, re.IGNORECASE):
            raise ValueError("Invalid OPML file: Unclosed <opml> element")

        if not re.search(r"<head[^>]*>", content, re.IGNORECASE):
            raise ValueError("Invalid OPML file: Missing <head> element")

        if not re.search(r"<body[^>]*>", content, re.IGNORECASE):
            raise ValueError("Invalid OPML file: Missing <body> element")

        if not re.search(r"<outline[^>]*>", content, re.IGNORECASE):
            raise ValueError(
                "Invalid OPML file: No <outline> elements found (no feeds to import)"
            )

        dangerous_patterns = [
            r"<\s*script[^>]*>",
            r"javascript\s*:",
            r"vbscript\s*:",
            r"data\s*:",
            r"<\s*iframe[^>]*>",
            r"<\s*object[^>]*>",
            r"<\s*embed[^>]*>",
            r"<!--.*?-->",
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                raise ValueError(
                    f"OPML file contains potentially unsafe content: {pattern}"
                )

        attr_pattern = r'(\w+)\s*=\s*["\']([^"\']*)["\']'
        for match in re.finditer(attr_pattern, content):
            attr_name, attr_value = match.groups()
            if len(attr_value) > MAX_OPML_ATTRIBUTE_LENGTH:
                raise ValueError(
                    f"OPML file has unusually long attribute value for '{attr_name}'"
                )

        current_depth = 0
        for line in content.split("\n"):
            open_count = len(
                re.findall(r"<outline\b[^/>]*>", line, re.IGNORECASE)
            )
            close_count = len(re.findall(r"</outline>", line, re.IGNORECASE))
            current_depth += open_count - close_count
            if current_depth > MAX_OPML_NESTING_DEPTH:
                raise ValueError(
                    f"OPML file has nesting depth greater than {MAX_OPML_NESTING_DEPTH}"
                )

        outline_count = len(
            re.findall(r"<outline[^>]*>", content, re.IGNORECASE)
        )
        if outline_count > MAX_OPML_OUTLINES:
            raise ValueError(
                f"OPML file has too many feeds ({outline_count}). Maximum allowed: {MAX_OPML_OUTLINES}"
            )

        return

    @classmethod
    def validate_opml_file_metadata(
        cls, file_content: bytes, filename: str
    ) -> tuple[str, int, str | None]:
        """Validate OPML file metadata and return decoded content."""
        from backend.utils.validators import (
            validate_file_size,
            validate_opml_filename,
        )

        validate_opml_filename(filename)

        file_size = len(file_content)
        validate_file_size(file_size, MAX_OPML_FILE_SIZE, "OPML file")

        file_content_str = None
        encoding_used = None

        for encoding in OpmlParser.ENCODINGS:
            try:
                target_encoding = (
                    "utf-8-sig" if encoding == "utf-8" else encoding
                )
                file_content_str = file_content.decode(target_encoding)
                file_content_str = file_content_str.lstrip("\ufeff")
                encoding_used = encoding
                break
            except UnicodeDecodeError:
                continue

        if file_content_str is None:
            raise ValueError(
                "Invalid file encoding. OPML files must be UTF-8, Windows-1252, ISO-8859-1, or UTF-16 encoded"
            )

        content_start = file_content_str.strip()[:200].lower()
        if not (
            content_start.startswith("<?xml")
            or content_start.startswith("<opml")
        ):
            raise ValueError("File does not appear to be a valid OPML file")

        try:
            cls.validate_opml_content(file_content_str)
        except ValueError as e:
            raise ValueError(f"Invalid OPML file: {e!s}") from e

        return file_content_str, file_size, encoding_used

    @classmethod
    def validate_file_age(cls, file_age_seconds: int) -> None:
        """Check if file has expired based on age."""
        max_age = OPML_FILE_EXPIRY_HOURS * 60 * 60
        if file_age_seconds > max_age:
            raise ValueError(
                f"Export file has expired ({OPML_FILE_EXPIRY_HOURS}-hour limit)"
            )
