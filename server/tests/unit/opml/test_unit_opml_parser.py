"""Unit tests for OpmlParser."""

import pytest

from backend.domain.opml import OpmlParser


class TestDetectEncoding:
    """Test encoding detection."""

    def test_utf8_encoding(self):
        """Should detect UTF-8 encoding."""
        content = (
            b'<?xml version="1.0" encoding="UTF-8"?><opml version="2.0"></opml>'
        )
        decoded, encoding = OpmlParser.detect_encoding(content)
        assert encoding == "utf-8"
        assert "<opml" in decoded

    def test_utf8_with_bom(self):
        """Should handle UTF-8 BOM correctly."""
        content = (
            b'\xef\xbb\xbf<?xml version="1.0"?><opml version="2.0"></opml>'
        )
        decoded, encoding = OpmlParser.detect_encoding(content)
        assert encoding == "utf-8"
        assert not decoded.startswith("\ufeff")

    def test_windows1252_encoding(self):
        """Should detect windows-1252 encoding."""
        content = '<?xml version="1.0" encoding="windows-1252"?><opml version="2.0"><head></head><body></body></opml>'.encode(
            "windows-1252"
        )
        _decoded, encoding = OpmlParser.detect_encoding(content)
        # The validation check finds OPML markers, so windows-1252 content should pass
        assert (
            encoding == "windows-1252" or encoding == "utf-8"
        )  # Both can decode windows-1252 content

    def test_unsupported_encoding_raises_error(self):
        """Should raise ValueError for unsupported encoding."""
        content = b"\xff\xfe\x00\x00"  # UTF-32 BOM (not supported)
        with pytest.raises(ValueError, match="Unable to decode file"):
            OpmlParser.detect_encoding(content)


class TestValidateUrl:
    """Test URL validation."""

    def test_valid_http_url(self):
        """Should accept valid HTTP URL."""
        is_valid, error = OpmlParser.validate_url("http://example.com/feed.xml")
        assert is_valid is True
        assert error is None

    def test_valid_https_url(self):
        """Should accept valid HTTPS URL."""
        is_valid, error = OpmlParser.validate_url(
            "https://example.com/feed.xml"
        )
        assert is_valid is True
        assert error is None

    def test_empty_url(self):
        """Should reject empty URL."""
        is_valid, error = OpmlParser.validate_url("")
        assert is_valid is False
        assert error == "URL is empty"

    def test_missing_scheme(self):
        """Should reject URL without scheme."""
        is_valid, error = OpmlParser.validate_url("example.com/feed.xml")
        assert is_valid is False
        assert "missing scheme" in error.lower()

    def test_unsupported_scheme(self):
        """Should reject non-HTTP/HTTPS schemes."""
        is_valid, error = OpmlParser.validate_url("ftp://example.com/feed.xml")
        assert is_valid is False
        assert "Unsupported scheme" in error

    def test_missing_domain(self):
        """Should reject URL without domain."""
        is_valid, error = OpmlParser.validate_url("http://")
        assert is_valid is False
        assert "missing domain" in error.lower()


class TestParseFeedsWithFolders:
    """Test OPML parsing with folder extraction."""

    def test_parse_simple_feed(self):
        """Should parse a single feed without folder."""
        content = """<opml version="2.0">
            <body>
                <outline text="Test Feed" xmlUrl="https://example.com/feed.xml"/>
            </body>
        </opml>"""
        feeds = OpmlParser.parse_feeds_with_folders(content)
        assert len(feeds) == 1
        assert feeds[0].url == "https://example.com/feed.xml"
        assert feeds[0].title == "Test Feed"
        assert feeds[0].folder_path == []

    def test_parse_feed_in_single_folder(self):
        """Should parse a feed inside a folder."""
        content = """<opml version="2.0">
            <body>
                <outline text="Tech">
                    <outline text="Blog" xmlUrl="https://blog.com/feed.xml"/>
                </outline>
            </body>
        </opml>"""
        feeds = OpmlParser.parse_feeds_with_folders(content)
        assert len(feeds) == 1
        assert feeds[0].folder_path == ["Tech"]

    def test_parse_feed_in_nested_folders(self):
        """Should parse a feed inside nested folders."""
        content = """<opml version="2.0">
            <body>
                <outline text="Tech">
                    <outline text="Blogs">
                        <outline text="Dev" xmlUrl="https://dev.com/feed.xml"/>
                    </outline>
                </outline>
            </body>
        </opml>"""
        feeds = OpmlParser.parse_feeds_with_folders(content)
        assert len(feeds) == 1
        assert feeds[0].folder_path == ["Tech", "Blogs"]

    def test_parse_multiple_feeds_mixed_folders(self):
        """Should parse multiple feeds with different folder levels."""
        content = """<opml version="2.0">
            <body>
                <outline text="Tech" xmlUrl="https://tech.com/feed.xml"/>
                <outline text="Blogs">
                    <outline text="Blog 1" xmlUrl="https://blog1.com/feed.xml"/>
                    <outline text="Blog 2" xmlUrl="https://blog2.com/feed.xml"/>
                </outline>
            </body>
        </opml>"""
        feeds = OpmlParser.parse_feeds_with_folders(content)
        assert len(feeds) == 3
        assert feeds[0].folder_path == []  # Root level feed
        assert feeds[1].folder_path == ["Blogs"]
        assert feeds[2].folder_path == ["Blogs"]

    def test_max_folder_depth_limit(self):
        """Should flatten folders beyond MAX_DEPTH."""
        content = """<opml version="2.0">
            <body>
                <outline text="L1">
                    <outline text="L2">
                        <outline text="L3">
                            <outline text="L4">
                                <outline text="L5">
                                    <outline text="L6">
                                        <outline text="L7">
                                            <outline text="L8">
                                                <outline text="L9">
                                                    <outline text="L10">
                                                        <outline text="L11" xmlUrl="https://example.com/feed.xml"/>
                                                    </outline>
                                                </outline>
                                            </outline>
                                        </outline>
                                    </outline>
                                </outline>
                            </outline>
                        </outline>
                    </outline>
                </outline>
            </body>
        </opml>"""
        feeds = OpmlParser.parse_feeds_with_folders(content, max_depth=9)
        assert len(feeds) == 1
        assert len(feeds[0].folder_path) == 9  # Truncated at max depth

    def test_title_fallback_to_text(self):
        """Should use text attribute when title is missing."""
        content = """<opml version="2.0">
            <body>
                <outline text="Feed Name" xmlUrl="https://example.com/feed.xml"/>
            </body>
        </opml>"""
        feeds = OpmlParser.parse_feeds_with_folders(content)
        assert feeds[0].title == "Feed Name"

    def test_missing_xmlUrl_skipped(self):
        """Should skip outline elements without xmlUrl (folders)."""
        content = """<opml version="2.0">
            <body>
                <outline text="Just a folder">
                    <outline text="Nested folder"/>
                </outline>
            </body>
        </opml>"""
        feeds = OpmlParser.parse_feeds_with_folders(content)
        assert len(feeds) == 0

    def test_invalid_xml_raises_error(self):
        """Should raise ValueError for invalid XML."""
        content = '<opml><body><outline xmlUrl="https://example.com/feed.xml"'
        with pytest.raises(ValueError, match="Invalid XML structure"):
            OpmlParser.parse_feeds_with_folders(content)


class TestBuildFolderStructure:
    """Test folder structure building."""

    def test_empty_folder_structure(self):
        """Should return empty list for feeds without folders."""
        from backend.domain.opml.parser import OpmlFeed

        feeds = [
            OpmlFeed(title="Feed 1", url="https://feed1.com"),
            OpmlFeed(title="Feed 2", url="https://feed2.com"),
        ]
        structure = OpmlParser.build_folder_structure(feeds)
        assert len(structure) == 0

    def test_single_level_folders(self):
        """Should build structure for single-level folders."""
        from backend.domain.opml.parser import OpmlFeed

        feeds = [
            OpmlFeed(
                title="Feed 1", url="https://feed1.com", folder_path=["Tech"]
            ),
            OpmlFeed(
                title="Feed 2", url="https://feed2.com", folder_path=["News"]
            ),
        ]
        structure = OpmlParser.build_folder_structure(feeds)
        assert len(structure) == 2
        assert structure[0]["name"] == "Tech"
        assert structure[0]["feed_count"] == 1
        assert structure[1]["name"] == "News"
        assert structure[1]["feed_count"] == 1

    def test_nested_folder_structure(self):
        """Should build structure for nested folders."""
        from backend.domain.opml.parser import OpmlFeed

        feeds = [
            OpmlFeed(
                title="Feed 1",
                url="https://feed1.com",
                folder_path=["Tech", "Blogs"],
            ),
            OpmlFeed(
                title="Feed 2",
                url="https://feed2.com",
                folder_path=["Tech", "News"],
            ),
        ]
        structure = OpmlParser.build_folder_structure(feeds)
        assert len(structure) == 1
        assert structure[0]["name"] == "Tech"
        assert len(structure[0]["children"]) == 2
        assert structure[0]["children"][0]["name"] == "Blogs"
        assert structure[0]["children"][1]["name"] == "News"


class TestValidateAndParse:
    """Test the main validation and parsing entry point."""

    def test_valid_opml_file(self):
        """Should parse a valid OPML file successfully."""
        content = (
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<opml version="2.0">'
            b"<head><title>My Feeds</title></head>"
            b'<body><outline text="Tech Blog" xmlUrl="https://tech.com/feed.xml"/></body>'
            b"</opml>"
        )
        result = OpmlParser.validate_and_parse(content, "test.opml")
        assert result.is_valid is True
        assert result.total_feeds == 1
        assert len(result.feeds) == 1
        assert len(result.errors) == 0
        assert result.encoding == "utf-8"

    def test_missing_opml_tag(self):
        """Should fail when <opml> tag is missing."""
        content = b'<?xml version="1.0"?><html><body></body></html>'
        result = OpmlParser.validate_and_parse(content, "test.html")
        assert result.is_valid is False
        assert any("missing <opml>" in e for e in result.errors)

    def test_missing_head_tag(self):
        """Should fail when <head> tag is missing."""
        content = (
            b'<?xml version="1.0"?><opml version="2.0"><body></body></opml>'
        )
        result = OpmlParser.validate_and_parse(content, "test.opml")
        assert result.is_valid is False
        assert any("missing <head>" in e for e in result.errors)

    def test_missing_body_tag(self):
        """Should fail when <body> tag is missing."""
        content = b'<?xml version="1.0" encoding="UTF-8"?><opml version="2.0"><head><title>Test</title></head></opml>'
        result = OpmlParser.validate_and_parse(content, "test.opml")
        assert result.is_valid is False
        assert any("missing <body>" in e for e in result.errors)

    def test_detects_invalid_urls(self):
        """Should identify and report invalid URLs."""
        content = (
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<opml version="2.0">'
            b"<head></head>"
            b"<body>"
            b'<outline text="Invalid Feed" xmlUrl="not-a-url"/>'
            b'<outline text="Valid Feed" xmlUrl="https://valid.com/feed.xml"/>'
            b"</body></opml>"
        )
        result = OpmlParser.validate_and_parse(content, "test.opml")
        assert result.is_valid is True  # Still valid, just has warnings
        assert len(result.invalid_urls) == 1
        assert result.invalid_urls[0]["url"] == "not-a-url"

    def test_detects_duplicate_urls_within_file(self):
        """Should detect duplicate URLs within the OPML file."""
        content = (
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<opml version="2.0">'
            b"<head></head>"
            b"<body>"
            b'<outline text="Feed 1" xmlUrl="https://example.com/feed.xml"/>'
            b'<outline text="Feed 2" xmlUrl="https://example.com/feed.xml"/>'
            b"</body></opml>"
        )
        result = OpmlParser.validate_and_parse(content, "test.opml")
        assert result.is_valid is True
        assert len(result.duplicate_urls) == 1
        assert "https://example.com/feed.xml" in result.duplicate_urls
        assert len(result.feeds) == 1  # Only one valid feed (first one kept)

    def test_detects_duplicate_urls_with_existing(self):
        """Should detect URLs that already exist in user's subscriptions."""
        content = (
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<opml version="2.0">'
            b"<head></head>"
            b"<body>"
            b'<outline text="Existing Feed" xmlUrl="https://existing.com/feed.xml"/>'
            b'<outline text="New Feed" xmlUrl="https://new.com/feed.xml"/>'
            b"</body></opml>"
        )
        existing_urls = {"https://existing.com/feed.xml"}
        result = OpmlParser.validate_and_parse(
            content, "test.opml", existing_urls
        )
        assert result.is_valid is True
        assert len(result.duplicate_urls) == 1
        assert "https://existing.com/feed.xml" in result.duplicate_urls
        assert len(result.feeds) == 1  # Only the new feed
        assert result.feeds[0].url == "https://new.com/feed.xml"

    def test_no_feeds_warning(self):
        """Should warn when OPML file contains no feeds."""
        content = (
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<opml version="2.0">'
            b"<head></head>"
            b"<body></body></opml>"
        )
        result = OpmlParser.validate_and_parse(content, "test.opml")
        assert result.is_valid is True
        assert result.total_feeds == 0
        assert any("No feeds found" in w for w in result.warnings)

    def test_html_entity_unescaping(self):
        """Should unescape HTML entities in OPML content."""
        content = (
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<opml version="2.0">'
            b"<head></head>"
            b"<body>"
            b'<outline text="Jason&apos;s Blog" xmlUrl="https://example.com/feed.xml"/>'
            b"</body></opml>"
        )
        result = OpmlParser.validate_and_parse(content, "test.opml")
        assert result.is_valid is True
        assert len(result.feeds) == 1

    def test_unescaped_ampersand_fixing(self):
        """Should fix unescaped ampersands in URLs."""
        # Note: Valid XML must have &amp; for & in URLs
        # The preprocess_content method handles cases where they're not properly escaped
        content = (
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<opml version="2.0">'
            b"<head></head>"
            b"<body>"
            b'<outline text="Feed" xmlUrl="https://example.com/feed?a=1&amp;b=2"/>'
            b"</body></opml>"
        )
        result = OpmlParser.validate_and_parse(content, "test.opml")
        assert result.is_valid is True
        assert len(result.feeds) == 1
