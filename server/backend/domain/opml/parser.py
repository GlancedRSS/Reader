"""OPML parser for feed extraction and structure analysis.

This module provides parsing functionality for OPML files, extracting
feeds with their folder hierarchy and providing detailed structure analysis.
"""

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

if TYPE_CHECKING:
    pass


@dataclass
class OpmlFeed:
    """Represents a single feed found in OPML.

    Attributes:
        title: Feed title (from title or text attribute).
        url: Feed URL (from xmlUrl attribute).
        html_url: Optional website URL (from htmlUrl attribute).
        folder_path: List of folder names representing the hierarchy.
        description: Optional feed description.

    """

    title: str | None
    url: str
    html_url: str | None = None
    folder_path: list[str] = field(default_factory=list)
    description: str | None = None


@dataclass
class FolderNode:
    """Represents a folder in the OPML structure.

    Attributes:
        name: Folder name (from text or title attribute).
        path: Full path from root (e.g., ["Tech", "Blogs"]).
        feeds: List of feeds directly in this folder.
        children: Child folders.

    """

    name: str
    path: list[str]
    feeds: list[OpmlFeed] = field(default_factory=list)
    children: dict[str, "FolderNode"] = field(default_factory=dict)


@dataclass
class OpmlValidationResult:
    """Result of OPML validation and parsing.

    Attributes:
        is_valid: Whether the OPML is valid.
        total_feeds: Total number of feeds found.
        folder_structure: List of folder info dictionaries.
        errors: List of error messages.
        warnings: List of warning messages.
        feeds: List of parsed feeds.
        encoding: Detected character encoding.
        duplicate_urls: Set of duplicate URLs found.
        invalid_urls: List of invalid URLs.

    """

    is_valid: bool
    total_feeds: int
    folder_structure: list[dict[str, Any]]
    errors: list[str]
    warnings: list[str]
    feeds: list[OpmlFeed]
    encoding: str
    duplicate_urls: set[str]
    invalid_urls: list[dict[str, Any]]


class OpmlParser:
    """Parser for OPML files with structure analysis.

    Handles:
    - Character encoding detection and decoding
    - XML parsing with error recovery
    - Feed extraction with folder hierarchy
    - URL validation (http/https only)
    - Duplicate detection
    - Folder structure analysis (flattening at max depth)
    """

    MAX_DEPTH = 9
    ENCODINGS = ["utf-8", "windows-1252", "iso-8859-1", "utf-16"]
    VALID_SCHEMES = {"http", "https"}

    @classmethod
    def detect_encoding(cls, content: bytes) -> tuple[str, str]:
        """Detect character encoding of OPML content.

        Args:
            content: Raw file content as bytes.

        Returns:
            Tuple of (decoded_content_string, encoding_name).

        Raises:
            ValueError: If unable to decode with any supported encoding.

        """
        for encoding in cls.ENCODINGS:
            try:
                target_encoding = (
                    "utf-8-sig" if encoding == "utf-8" else encoding
                )
                decoded = content.decode(target_encoding)
                decoded = decoded.lstrip("\ufeff")
                if any(
                    marker in decoded[:1000].lower()
                    for marker in ["<?xml", "<opml", "<opml"]
                ):
                    return decoded, encoding
            except UnicodeDecodeError:
                continue

        raise ValueError(
            "Unable to decode file - unsupported encoding. "
            f"Supported encodings: {', '.join(cls.ENCODINGS)}"
        )

    @classmethod
    def preprocess_content(cls, content: str) -> str:
        """Preprocess OPML content to handle common issues.

        Args:
            content: Decoded OPML content string.

        Returns:
            Preprocessed content string.

        """
        return re.sub(
            r'(<outline[^>]*(?:xmlUrl|htmlUrl)="[^"]*)&(?=[a-z0-9]+)([^"]*")',
            r"\1&amp;\2",
            content,
            flags=re.IGNORECASE,
        )

    @classmethod
    def validate_url(cls, url: str | None) -> tuple[bool, str | None]:
        """Validate that a URL is http/https and well-formed.

        Args:
            url: URL string to validate.

        Returns:
            Tuple of (is_valid, error_message).

        """
        if not url or not url.strip():
            return False, "URL is empty"

        url = url.strip()

        try:
            parsed = urlparse(url)

            if not parsed.scheme:
                return False, "URL missing scheme (e.g., http://)"

            if parsed.scheme.lower() not in cls.VALID_SCHEMES:
                return (
                    False,
                    f"Unsupported scheme: {parsed.scheme}. Only http/https allowed.",
                )

            if not parsed.netloc:
                return False, "URL missing domain"

            return True, None

        except Exception as e:
            return False, f"Invalid URL: {e!s}"

    @classmethod
    def parse_feeds_with_folders(
        cls, content: str, max_depth: int = MAX_DEPTH
    ) -> list[OpmlFeed]:
        """Parse OPML content and extract feeds with folder paths.

        Args:
            content: Preprocessed OPML content string.
            max_depth: Maximum folder depth before flattening.

        Returns:
            List of OpmlFeed objects with folder_path populated.

        """
        content = (
            content.split("?>", 1)[-1] if "?>" in content[:100] else content
        )

        try:
            root = ET.fromstring(f"<root>{content}</root>")
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML structure: {e!s}") from e

        feeds: list[OpmlFeed] = []

        for outline in root.findall(".//outline[@xmlUrl]"):
            url = outline.get("xmlUrl")
            if not url:
                continue

            title = (
                outline.get("title")
                or outline.get("text")
                or outline.get("title")
            )
            html_url = outline.get("htmlUrl")
            description = outline.get("description")

            folder_path: list[str] = []
            current = outline
            depth = 0

            while (
                parent := cls._find_parent_outline(root, current)
            ) is not None:
                parent_title = parent.get("title") or parent.get("text")
                if parent_title:
                    folder_path.insert(0, parent_title)
                    depth += 1
                    if depth >= max_depth:
                        break
                current = parent

            feed = OpmlFeed(
                title=title,
                url=url,
                html_url=html_url,
                folder_path=folder_path,
                description=description,
            )
            feeds.append(feed)

        return feeds

    @classmethod
    def _find_parent_outline(
        cls, root: ET.Element, element: ET.Element
    ) -> ET.Element | None:
        """Find the parent outline element of a given element.

        Args:
            root: Root element to search from.
            element: Element to find parent for.

        Returns:
            Parent outline element or None if not found.

        """
        for outline in root.findall(".//outline"):
            if element in list(outline):
                return outline
        return None

    @classmethod
    def build_folder_structure(
        cls, feeds: list[OpmlFeed], max_depth: int = MAX_DEPTH
    ) -> list[dict[str, Any]]:
        """Build folder structure from feeds with folder paths.

        Args:
            feeds: List of OpmlFeed objects.
            max_depth: Maximum folder depth.

        Returns:
            List of folder info dictionaries.

        """
        root_folders: dict[str, FolderNode] = {}

        for feed in feeds:
            if not feed.folder_path:
                continue

            folder_path = feed.folder_path[:max_depth]
            current_level = root_folders

            for depth, folder_name in enumerate(folder_path):
                if folder_name not in current_level:
                    path = folder_path[: depth + 1]
                    node = FolderNode(name=folder_name, path=path)
                    current_level[folder_name] = node

                current_node = current_level[folder_name]

                if depth == len(folder_path) - 1:
                    current_node.feeds.append(feed)

                current_level = current_node.children

        return [
            cls._folder_node_to_dict(node) for node in root_folders.values()
        ]

    @classmethod
    def _folder_node_to_dict(cls, node: FolderNode) -> dict[str, Any]:
        """Convert FolderNode to dictionary.

        Args:
            node: FolderNode to convert.

        Returns:
            Dictionary representation.

        """
        return {
            "name": node.name,
            "path": "/".join(node.path),
            "feed_count": len(node.feeds),
            "children": [
                cls._folder_node_to_dict(child)
                for child in node.children.values()
            ],
        }

    @classmethod
    def validate_and_parse(
        cls,
        file_content: bytes,
        filename: str,
        existing_urls: set[str] | None = None,
    ) -> OpmlValidationResult:
        """Validate and parse OPML file content.

        This is the main entry point for OPML validation. It:
        1. Detects character encoding
        2. Preprocesses content (fixes common issues)
        3. Validates structure
        4. Extracts feeds with folder paths
        5. Validates URLs
        6. Detects duplicates
        7. Builds folder structure

        Args:
            file_content: Raw file content as bytes.
            filename: Original filename.
            existing_urls: Set of URLs the user is already subscribed to.

        Returns:
            OpmlValidationResult with detailed analysis.

        """
        errors: list[str] = []
        warnings: list[str] = []
        feeds: list[OpmlFeed] = []
        duplicate_urls: set[str] = set()
        invalid_urls: list[dict[str, str]] = []

        try:
            content, encoding = cls.detect_encoding(file_content)
        except ValueError as e:
            return OpmlValidationResult(
                is_valid=False,
                total_feeds=0,
                folder_structure=[],
                errors=[str(e)],
                warnings=[],
                feeds=[],
                encoding="unknown",
                duplicate_urls=set(),
                invalid_urls=[],
            )

        content = cls.preprocess_content(content)

        content_lower = content.lower()
        if "<opml" not in content_lower:
            errors.append("Not an OPML file - missing <opml> tag")

        if "<head>" not in content_lower:
            errors.append("Invalid OPML structure - missing <head>")

        if "<body>" not in content_lower:
            errors.append("Invalid OPML structure - missing <body>")

        if errors:
            return OpmlValidationResult(
                is_valid=False,
                total_feeds=0,
                folder_structure=[],
                errors=errors,
                warnings=warnings,
                feeds=[],
                encoding=encoding,
                duplicate_urls=set(),
                invalid_urls=[],
            )

        try:
            feeds = cls.parse_feeds_with_folders(content)
        except ValueError as e:
            return OpmlValidationResult(
                is_valid=False,
                total_feeds=0,
                folder_structure=[],
                errors=[str(e)],
                warnings=warnings,
                feeds=[],
                encoding=encoding,
                duplicate_urls=set(),
                invalid_urls=[],
            )

        if not feeds:
            warnings.append("No feeds found in OPML file")

        seen_urls: set[str] = set()
        valid_feeds: list[OpmlFeed] = []

        for feed in feeds:
            is_valid, error_msg = cls.validate_url(feed.url)
            if not is_valid:
                title: str = feed.title if feed.title else "Unknown"
                error: str = error_msg if error_msg else "Unknown error"
                invalid_urls.append(
                    {"url": feed.url, "title": title, "error": error}
                )
                continue

            if feed.url in seen_urls:
                duplicate_urls.add(feed.url)
                continue

            if existing_urls and feed.url in existing_urls:
                duplicate_urls.add(feed.url)
                continue

            seen_urls.add(feed.url)
            valid_feeds.append(feed)

        folder_structure = cls.build_folder_structure(valid_feeds)

        if invalid_urls:
            warnings.append(
                f"{len(invalid_urls)} feeds have invalid URLs and will be skipped"
            )

        if duplicate_urls:
            warnings.append(
                f"{len(duplicate_urls)} feeds are duplicates and will be skipped"
            )

        return OpmlValidationResult(
            is_valid=len(errors) == 0,
            total_feeds=len(feeds),
            folder_structure=folder_structure,
            errors=errors,
            warnings=warnings,
            feeds=valid_feeds,
            encoding=encoding,
            duplicate_urls=duplicate_urls,
            invalid_urls=invalid_urls,
        )
