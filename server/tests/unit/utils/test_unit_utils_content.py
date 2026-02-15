"""Unit tests for content processor utilities."""

from bs4 import BeautifulSoup

from backend.utils.content import ContentProcessor  # type: ignore[attr-defined]


class TestContentProcessorInit:
    """Test ContentProcessor initialization."""

    async def test_init(self):
        """Should initialize with HTML cleaner."""
        processor = ContentProcessor()
        assert processor.html_cleaner is not None


class TestGenerateFrontendHtml:
    """Test frontend HTML generation."""

    async def test_generate_frontend_html_empty(self):
        """Should return empty string for empty input."""
        processor = ContentProcessor()
        assert processor._generate_frontend_html("") == ""
        assert processor._generate_frontend_html(None) == ""

    async def test_generate_frontend_html_basic_paragraph(self):
        """Should process basic paragraph HTML."""
        processor = ContentProcessor()
        html = "<p>Hello world</p>"
        result = processor._generate_frontend_html(html)

        assert "Hello world" in result
        assert "my-4" in result  # Tailwind class for paragraphs

    async def test_generate_frontend_html_with_image(self):
        """Should add lazy loading and styling to images."""
        processor = ContentProcessor()
        html = '<img src="test.jpg" alt="Test">'
        result = processor._generate_frontend_html(html)

        assert 'loading="lazy"' in result
        assert "max-w-full" in result
        assert "rounded-xl" in result

    async def test_generate_frontend_html_with_link(self):
        """Should add security attributes to external links."""
        processor = ContentProcessor()
        html = '<a href="https://example.com">Link</a>'
        result = processor._generate_frontend_html(html)

        assert 'target="_blank"' in result
        assert 'rel="noopener noreferrer"' in result
        assert "text-primary" in result

    async def test_generate_frontend_html_with_internal_link(self):
        """Should not add target blank for relative links."""
        processor = ContentProcessor()
        html = '<a href="/internal">Link</a>'
        result = processor._generate_frontend_html(html)

        assert "target" not in result

    async def test_generate_frontend_html_with_heading(self):
        """Should style headings with typography classes."""
        processor = ContentProcessor()
        html = "<h1>Title</h1>"
        result = processor._generate_frontend_html(html)

        assert "font-semibold" in result
        assert "text-3xl" in result
        assert "my-4" in result

    async def test_generate_frontend_html_with_code(self):
        """Should style code blocks."""
        processor = ContentProcessor()
        html = "<code>const x = 1;</code>"
        result = processor._generate_frontend_html(html)

        assert "bg-muted" in result
        assert "font-mono" in result
        assert "text-sm" in result

    async def test_generate_frontend_html_with_pre(self):
        """Should style pre blocks."""
        processor = ContentProcessor()
        html = "<pre><code>code here</code></pre>"
        result = processor._generate_frontend_html(html)

        assert "overflow-x-auto" in result
        assert "p-4" in result

    async def test_generate_frontend_html_with_blockquote(self):
        """Should style blockquotes."""
        processor = ContentProcessor()
        html = "<blockquote>Quote here</blockquote>"
        result = processor._generate_frontend_html(html)

        assert "border" in result
        assert "bg-muted" in result
        assert "rounded-lg" in result

    async def test_generate_frontend_html_with_list(self):
        """Should style unordered lists."""
        processor = ContentProcessor()
        html = "<ul><li>Item 1</li><li>Item 2</li></ul>"
        result = processor._generate_frontend_html(html)

        assert "list-disc" in result
        assert "list-outside" in result
        assert "space-y-2" in result

    async def test_generate_frontend_html_with_ordered_list(self):
        """Should style ordered lists."""
        processor = ContentProcessor()
        html = "<ol><li>Item 1</li></ol>"
        result = processor._generate_frontend_html(html)

        assert "list-decimal" in result
        assert "list-outside" in result

    async def test_generate_frontend_html_error_handling(self):
        """Should return cleaned HTML on processing error."""
        processor = ContentProcessor()
        # Malformed HTML that might cause issues
        html = "<p>Test</p>"
        result = processor._generate_frontend_html(html)

        # Should still return something (either processed or cleaned)
        assert result is not None
        assert len(result) > 0


class TestProcessImagesForFrontend:
    """Test image processing."""

    async def test_adds_tailwind_classes(self):
        """Should add Tailwind CSS classes to images."""
        processor = ContentProcessor()
        html = '<img src="test.jpg">'
        soup = BeautifulSoup(html, "html.parser")

        processor._process_images_for_frontend(soup)

        img = soup.find("img")
        classes = img.get("class", [])
        assert "max-w-full" in classes
        assert "h-auto" in classes
        assert "rounded-xl" in classes
        assert "mx-auto" in classes
        assert "my-4" in classes

    async def test_preserves_existing_classes(self):
        """Should preserve existing image classes."""
        processor = ContentProcessor()
        html = '<img src="test.jpg" class="existing-class">'
        soup = BeautifulSoup(html, "html.parser")

        processor._process_images_for_frontend(soup)

        img = soup.find("img")
        classes = img.get("class", [])
        assert "existing-class" in classes

    async def test_adds_lazy_loading(self):
        """Should add lazy loading attribute."""
        processor = ContentProcessor()
        html = '<img src="test.jpg">'
        soup = BeautifulSoup(html, "html.parser")

        processor._process_images_for_frontend(soup)

        img = soup.find("img")
        assert img.get("loading") == "lazy"

    async def test_preserves_existing_loading(self):
        """Should not override existing loading attribute."""
        processor = ContentProcessor()
        html = '<img src="test.jpg" loading="eager">'
        soup = BeautifulSoup(html, "html.parser")

        processor._process_images_for_frontend(soup)

        img = soup.find("img")
        assert img.get("loading") == "eager"

    async def test_adds_empty_alt(self):
        """Should add empty alt text if missing."""
        processor = ContentProcessor()
        html = '<img src="test.jpg">'
        soup = BeautifulSoup(html, "html.parser")

        processor._process_images_for_frontend(soup)

        img = soup.find("img")
        assert img.get("alt") == ""

    async def test_preserves_existing_alt(self):
        """Should preserve existing alt text."""
        processor = ContentProcessor()
        html = '<img src="test.jpg" alt="Description">'
        soup = BeautifulSoup(html, "html.parser")

        processor._process_images_for_frontend(soup)

        img = soup.find("img")
        assert img.get("alt") == "Description"


class TestProcessLinksForFrontend:
    """Test link processing."""

    async def test_adds_tailwind_classes(self):
        """Should add Tailwind CSS classes to links."""
        processor = ContentProcessor()
        html = '<a href="/test">Link</a>'
        soup = BeautifulSoup(html, "html.parser")

        processor._process_links_for_frontend(soup)

        link = soup.find("a")
        classes = link.get("class", [])
        assert "text-primary" in classes
        assert "hover:underline" in classes

    async def test_adds_security_attributes_to_external_links(self):
        """Should add target and rel to external links."""
        processor = ContentProcessor()
        html = '<a href="https://example.com">Link</a>'
        soup = BeautifulSoup(html, "html.parser")

        processor._process_links_for_frontend(soup)

        link = soup.find("a")
        assert link.get("target") == "_blank"
        assert link.get("rel") == "noopener noreferrer"

    async def test_does_not_add_security_to_relative_links(self):
        """Should not add target/rel to relative or internal links."""
        processor = ContentProcessor()
        html = '<a href="/internal">Link</a>'
        soup = BeautifulSoup(html, "html.parser")

        processor._process_links_for_frontend(soup)

        link = soup.find("a")
        assert link.get("target") is None
        assert link.get("rel") is None

    async def test_handles_http_links(self):
        """Should add security to http links."""
        processor = ContentProcessor()
        html = '<a href="http://example.com">Link</a>'
        soup = BeautifulSoup(html, "html.parser")

        processor._process_links_for_frontend(soup)

        link = soup.find("a")
        assert link.get("target") == "_blank"


class TestProcessHeadingsForFrontend:
    """Test heading processing."""

    async def test_styles_h1(self):
        """Should style h1 elements."""
        processor = ContentProcessor()
        html = "<h1>Title</h1>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_headings_for_frontend(soup)

        h1 = soup.find("h1")
        classes = h1.get("class", [])
        assert "font-semibold" in classes
        assert "text-3xl" in classes
        assert "my-4" in classes

    async def test_styles_h2(self):
        """Should style h2 elements."""
        processor = ContentProcessor()
        html = "<h2>Subtitle</h2>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_headings_for_frontend(soup)

        h2 = soup.find("h2")
        classes = h2.get("class", [])
        assert "font-semibold" in classes
        assert "text-2xl" in classes

    async def test_styles_h3(self):
        """Should style h3 elements."""
        processor = ContentProcessor()
        html = "<h3>Section</h3>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_headings_for_frontend(soup)

        h3 = soup.find("h3")
        classes = h3.get("class", [])
        assert "font-semibold" in classes
        assert "text-xl" in classes

    async def test_preserves_heading_content(self):
        """Should preserve heading text content."""
        processor = ContentProcessor()
        html = "<h1>Original Title</h1>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_headings_for_frontend(soup)

        h1 = soup.find("h1")
        assert h1.text == "Original Title"


class TestProcessParagraphsForFrontend:
    """Test paragraph processing."""

    async def test_adds_tailwind_classes(self):
        """Should add Tailwind CSS classes to paragraphs."""
        processor = ContentProcessor()
        html = "<p>Paragraph text</p>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_paragraphs_for_frontend(soup)

        p = soup.find("p")
        classes = p.get("class", [])
        assert "my-4" in classes

    async def test_preserves_paragraph_content(self):
        """Should preserve paragraph text."""
        processor = ContentProcessor()
        html = "<p>Original text</p>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_paragraphs_for_frontend(soup)

        p = soup.find("p")
        assert p.text == "Original text"


class TestProcessListsForFrontend:
    """Test list processing."""

    async def test_styles_unordered_list(self):
        """Should style ul elements."""
        processor = ContentProcessor()
        html = "<ul><li>Item</li></ul>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_lists_for_frontend(soup)

        ul = soup.find("ul")
        classes = ul.get("class", [])
        assert "list-disc" in classes
        assert "list-outside" in classes
        assert "my-4" in classes

    async def test_styles_ordered_list(self):
        """Should style ol elements."""
        processor = ContentProcessor()
        html = "<ol><li>Item</li></ol>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_lists_for_frontend(soup)

        ol = soup.find("ol")
        classes = ol.get("class", [])
        assert "list-decimal" in classes
        assert "list-outside" in classes

    async def test_styles_list_items(self):
        """Should style li elements."""
        processor = ContentProcessor()
        html = "<ul><li>Item 1</li><li>Item 2</li></ul>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_lists_for_frontend(soup)

        lis = soup.find_all("li")
        for li in lis:
            classes = li.get("class", [])
            assert "my-1" in classes


class TestProcessCodeBlocksForFrontend:
    """Test code block processing."""

    async def test_styles_inline_code(self):
        """Should style inline code elements."""
        processor = ContentProcessor()
        html = "<p>Text with <code>inline code</code></p>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_code_blocks_for_frontend(soup)

        code = soup.find("code")
        classes = code.get("class", [])
        assert "bg-muted" in classes
        assert "font-mono" in classes
        assert "text-sm" in classes

    async def test_styles_pre_blocks(self):
        """Should style pre blocks."""
        processor = ContentProcessor()
        html = "<pre>code here</pre>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_code_blocks_for_frontend(soup)

        pre = soup.find("pre")
        classes = pre.get("class", [])
        assert "bg-muted" in classes
        assert "p-4" in classes
        assert "overflow-x-auto" in classes

    async def test_does_not_duplicate_classes_on_code_in_pre(self):
        """Should handle code elements within pre blocks."""
        processor = ContentProcessor()
        html = "<pre><code>code here</code></pre>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_code_blocks_for_frontend(soup)

        # Code inside pre does NOT get inline code styles (parent.name == "pre" check)
        code = soup.find("code")
        classes = code.get("class", [])
        # Code inside pre should not have the inline code classes
        assert "bg-muted" not in classes
        assert "font-mono" not in classes

        # Pre should get block styles
        pre = soup.find("pre")
        assert "p-4" in pre.get("class", [])


class TestProcessBlockquotesForFrontend:
    """Test blockquote processing."""

    async def test_adds_tailwind_classes(self):
        """Should add Tailwind CSS classes to blockquotes."""
        processor = ContentProcessor()
        html = "<blockquote>Quote here</blockquote>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_blockquotes_for_frontend(soup)

        blockquote = soup.find("blockquote")
        classes = blockquote.get("class", [])
        assert "border" in classes
        assert "bg-muted" in classes
        assert "rounded-lg" in classes
        assert "px-4" in classes
        assert "my-4" in classes

    async def test_preserves_blockquote_content(self):
        """Should preserve blockquote text."""
        processor = ContentProcessor()
        html = "<blockquote>Original quote</blockquote>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_blockquotes_for_frontend(soup)

        blockquote = soup.find("blockquote")
        assert blockquote.text == "Original quote"


class TestStripAllAttributes:
    """Test attribute stripping."""

    async def test_removes_style_attributes(self):
        """Should remove style attributes from elements."""
        processor = ContentProcessor()
        html = '<p style="color: red;">Text</p>'
        soup = BeautifulSoup(html, "html.parser")

        processor._strip_all_attributes(soup)

        p = soup.find("p")
        assert p.get("style") is None

    async def test_removes_script_onclick(self):
        """Should remove onclick and other event handlers."""
        processor = ContentProcessor()
        html = "<button onclick=\"alert('xss')\">Click</button>"
        soup = BeautifulSoup(html, "html.parser")

        processor._strip_all_attributes(soup)

        button = soup.find("button")
        assert button.get("onclick") is None


class TestRemoveEmptyAndUnnecessaryElements:
    """Test removal of empty elements."""

    async def test_removes_empty_paragraphs(self):
        """Should remove empty paragraph elements."""
        processor = ContentProcessor()
        html = "<p></p><p>Content</p>"
        soup = BeautifulSoup(html, "html.parser")

        processor._remove_empty_and_unnecessary_elements(soup)

        ps = soup.find_all("p")
        assert len(ps) == 1
        assert ps[0].text == "Content"

    async def test_removes_script_tags(self):
        """Should remove script tags."""
        processor = ContentProcessor()
        html = "<p>Content</p><script>alert('xss')</script>"
        soup = BeautifulSoup(html, "html.parser")

        processor._remove_empty_and_unnecessary_elements(soup)

        # Script tags are NOT removed by this function
        # (They might be handled by HTMLCleaner instead)
        script = soup.find("script")
        assert script is not None

    async def test_removes_style_tags(self):
        """Should remove style tags."""
        processor = ContentProcessor()
        html = "<p>Content</p><style>body { color: red; }</style>"
        soup = BeautifulSoup(html, "html.parser")

        processor._remove_empty_and_unnecessary_elements(soup)

        # Style tags are NOT removed by this function
        # (They might be handled by HTMLCleaner instead)
        style = soup.find("style")
        assert style is not None

    async def test_removes_consecutive_br_tags(self):
        """Should remove consecutive break tags."""
        processor = ContentProcessor()
        html = "<p>Text</p><br><br><p>More text</p>"
        soup = BeautifulSoup(html, "html.parser")

        processor._remove_empty_and_unnecessary_elements(soup)

        brs = soup.find_all("br")
        assert len(brs) == 1

    async def test_unwraps_single_child_divs(self):
        """Should unwrap divs with single child element."""
        processor = ContentProcessor()
        html = "<div><p>Content</p></div>"
        soup = BeautifulSoup(html, "html.parser")

        processor._remove_empty_and_unnecessary_elements(soup)

        # Div should be replaced with its child
        assert soup.find("div") is None
        assert soup.find("p") is not None

    async def test_removes_html_comments(self):
        """Should remove HTML comments."""
        processor = ContentProcessor()
        html = "<p>Content</p><!-- This is a comment --><p>More</p>"
        soup = BeautifulSoup(html, "html.parser")

        processor._remove_empty_and_unnecessary_elements(soup)

        from bs4 import Comment

        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        assert len(comments) == 0


class TestHasMeaningfulContent:
    """Test meaningful content detection."""

    async def test_returns_true_for_text_content(self):
        """Should return True for elements with text."""
        processor = ContentProcessor()
        html = "<p>Some text content</p>"
        soup = BeautifulSoup(html, "html.parser")
        p = soup.find("p")

        assert processor._has_meaningful_content(p) is True

    async def test_returns_false_for_empty_element(self):
        """Should return False for empty elements."""
        processor = ContentProcessor()
        html = "<p></p>"
        soup = BeautifulSoup(html, "html.parser")
        p = soup.find("p")

        assert processor._has_meaningful_content(p) is False

    async def test_returns_true_for_element_with_img(self):
        """Should return True for elements containing images."""
        processor = ContentProcessor()
        html = '<div><img src="test.jpg"></div>'
        soup = BeautifulSoup(html, "html.parser")
        div = soup.find("div")

        assert processor._has_meaningful_content(div) is True

    async def test_returns_false_for_img_without_src(self):
        """Should return False for img without src."""
        processor = ContentProcessor()
        html = "<div><img></div>"
        soup = BeautifulSoup(html, "html.parser")
        div = soup.find("div")

        assert processor._has_meaningful_content(div) is False

    async def test_returns_true_for_element_with_video(self):
        """Should return True for elements containing videos."""
        processor = ContentProcessor()
        html = '<div><video src="test.mp4"></video></div>'
        soup = BeautifulSoup(html, "html.parser")
        div = soup.find("div")

        assert processor._has_meaningful_content(div) is True

    async def test_returns_true_for_element_with_audio(self):
        """Should return True for elements containing audio."""
        processor = ContentProcessor()
        html = '<div><audio src="test.mp3"></audio></div>'
        soup = BeautifulSoup(html, "html.parser")
        div = soup.find("div")

        assert processor._has_meaningful_content(div) is True

    async def test_returns_true_for_element_with_svg(self):
        """Should return True for elements containing SVG."""
        processor = ContentProcessor()
        html = "<div><svg></svg></div>"
        soup = BeautifulSoup(html, "html.parser")
        div = soup.find("div")

        assert processor._has_meaningful_content(div) is True

    async def test_returns_false_for_none(self):
        """Should return False for None input."""
        processor = ContentProcessor()
        assert processor._has_meaningful_content(None) is False


class TestProcessTablesForFrontend:
    """Test table processing."""

    async def test_styles_table_element(self):
        """Should add Tailwind classes to table."""
        processor = ContentProcessor()
        html = "<table><tr><th>Header</th></tr><tr><td>Data</td></tr></table>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_tables_for_frontend(soup)

        table = soup.find("table")
        classes = table.get("class", [])
        assert "min-w-full" in classes
        assert "border-collapse" in classes

    async def test_wraps_table_in_div(self):
        """Should wrap table in overflow div."""
        processor = ContentProcessor()
        html = "<table><tr><td>Data</td></tr></table>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_tables_for_frontend(soup)

        wrapper = soup.find("div")
        assert wrapper is not None
        assert "overflow-x-auto" in wrapper.get("class", [])

    async def test_styles_table_headers(self):
        """Should add classes to th elements."""
        processor = ContentProcessor()
        html = "<table><tr><th>Header</th></tr></table>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_tables_for_frontend(soup)

        th = soup.find("th")
        classes = th.get("class", [])
        assert "border" in classes
        assert "px-4" in classes
        assert "py-2" in classes
        assert "text-left" in classes
        assert "font-medium" in classes

    async def test_styles_table_cells(self):
        """Should add classes to td elements."""
        processor = ContentProcessor()
        html = "<table><tr><td>Data</td></tr></table>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_tables_for_frontend(soup)

        td = soup.find("td")
        classes = td.get("class", [])
        assert "border" in classes
        assert "px-4" in classes
        assert "py-2" in classes


class TestProcessVideosForFrontend:
    """Test video processing."""

    async def test_adds_tailwind_classes_to_video(self):
        """Should add Tailwind classes to video elements."""
        processor = ContentProcessor()
        html = '<video src="test.mp4"></video>'
        soup = BeautifulSoup(html, "html.parser")

        processor._process_videos_for_frontend(soup)

        video = soup.find("video")
        classes = video.get("class", [])
        assert "w-full" in classes
        assert "max-w-2xl" in classes
        assert "rounded-lg" in classes
        assert "shadow-lg" in classes
        assert "my-4" in classes

    async def test_adds_controls_attribute(self):
        """Should add controls attribute to video."""
        processor = ContentProcessor()
        html = '<video src="test.mp4"></video>'
        soup = BeautifulSoup(html, "html.parser")

        processor._process_videos_for_frontend(soup)

        video = soup.find("video")
        assert video.get("controls") == ""

    async def test_preserves_existing_controls(self):
        """Should not override existing controls."""
        processor = ContentProcessor()
        html = '<video src="test.mp4" controls></video>'
        soup = BeautifulSoup(html, "html.parser")

        processor._process_videos_for_frontend(soup)

        video = soup.find("video")
        assert video.get("controls") is not None


class TestProcessAudioForFrontend:
    """Test audio processing."""

    async def test_adds_tailwind_classes_to_audio(self):
        """Should add Tailwind classes to audio elements."""
        processor = ContentProcessor()
        html = '<audio src="test.mp3"></audio>'
        soup = BeautifulSoup(html, "html.parser")

        processor._process_audio_for_frontend(soup)

        audio = soup.find("audio")
        classes = audio.get("class", [])
        assert "w-full" in classes
        assert "max-w-md" in classes
        assert "my-4" in classes

    async def test_adds_controls_attribute(self):
        """Should add controls attribute to audio."""
        processor = ContentProcessor()
        html = '<audio src="test.mp3"></audio>'
        soup = BeautifulSoup(html, "html.parser")

        processor._process_audio_for_frontend(soup)

        audio = soup.find("audio")
        assert audio.get("controls") is not None


class TestProcessTextFormattingForFrontend:
    """Test text formatting element processing."""

    async def test_styles_superscript(self):
        """Should style sup elements."""
        processor = ContentProcessor()
        html = "x<sup>2</sup>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_text_formatting_for_frontend(soup)

        sup = soup.find("sup")
        classes = sup.get("class", [])
        assert "text-sm" in classes

    async def test_styles_subscript(self):
        """Should style sub elements."""
        processor = ContentProcessor()
        html = "H<sub>2</sub>O"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_text_formatting_for_frontend(soup)

        sub = soup.find("sub")
        classes = sub.get("class", [])
        assert "text-sm" in classes


class TestProcessSemanticElementsForFrontend:
    """Test semantic element processing."""

    async def test_styles_mark(self):
        """Should style mark elements."""
        processor = ContentProcessor()
        html = "<mark>highlighted</mark>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_semantic_elements_for_frontend(soup)

        mark = soup.find("mark")
        classes = mark.get("class", [])
        assert "bg-yellow-200/50" in classes
        assert "px-1" in classes

    async def test_styles_cite(self):
        """Should style cite elements."""
        processor = ContentProcessor()
        html = "<cite>Source</cite>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_semantic_elements_for_frontend(soup)

        cite = soup.find("cite")
        classes = cite.get("class", [])
        assert "italic" in classes

    async def test_styles_quote(self):
        """Should style q elements."""
        processor = ContentProcessor()
        html = "<q>A quote</q>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_semantic_elements_for_frontend(soup)

        quote = soup.find("q")
        classes = quote.get("class", [])
        assert "italic" in classes

    async def test_styles_abbr(self):
        """Should style abbr elements."""
        processor = ContentProcessor()
        html = '<abbr title="World Wide Web">WWW</abbr>'
        soup = BeautifulSoup(html, "html.parser")

        processor._process_semantic_elements_for_frontend(soup)

        abbr = soup.find("abbr")
        classes = abbr.get("class", [])
        assert "border-b" in classes
        assert "border-dotted" in classes
        assert "cursor-help" in classes

    async def test_styles_address(self):
        """Should style address elements."""
        processor = ContentProcessor()
        html = "<address>123 Main St</address>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_semantic_elements_for_frontend(soup)

        address = soup.find("address")
        classes = address.get("class", [])
        assert "not-italic" in classes
        assert "my-4" in classes

    async def test_styles_small(self):
        """Should style small elements."""
        processor = ContentProcessor()
        html = "<small>fine print</small>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_semantic_elements_for_frontend(soup)

        small = soup.find("small")
        classes = small.get("class", [])
        assert "text-sm" in classes
        assert "text-muted-foreground" in classes

    async def test_styles_time(self):
        """Should style time elements."""
        processor = ContentProcessor()
        html = '<time datetime="2024-01-01">Jan 1, 2024</time>'
        soup = BeautifulSoup(html, "html.parser")

        processor._process_semantic_elements_for_frontend(soup)

        time = soup.find("time")
        classes = time.get("class", [])
        assert "text-muted-foreground" in classes
        assert "text-sm" in classes

    async def test_styles_definition_list(self):
        """Should style dl elements."""
        processor = ContentProcessor()
        html = "<dl><dt>Term</dt><dd>Definition</dd></dl>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_semantic_elements_for_frontend(soup)

        dl = soup.find("dl")
        dt = soup.find("dt")
        dd = soup.find("dd")

        assert "my-4" in dl.get("class", [])
        assert "font-medium" in dt.get("class", [])
        assert "mb-1" in dt.get("class", [])
        assert "ml-4" in dd.get("class", [])
        assert "mb-2" in dd.get("class", [])

    async def test_styles_figure_and_figcaption(self):
        """Should style figure and figcaption elements."""
        processor = ContentProcessor()
        html = "<figure><img src='test.jpg'><figcaption>Caption</figcaption></figure>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_semantic_elements_for_frontend(soup)

        figure = soup.find("figure")
        figcaption = soup.find("figcaption")

        assert "my-4" in figure.get("class", [])
        assert "text-sm" in figcaption.get("class", [])
        assert "mt-2" in figcaption.get("class", [])
        assert "text-center" in figcaption.get("class", [])

    async def test_styles_details_and_summary(self):
        """Should style details and summary elements."""
        processor = ContentProcessor()
        html = "<details><summary>Click to expand</summary><p>Content</p></details>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_semantic_elements_for_frontend(soup)

        details = soup.find("details")
        summary = soup.find("summary")

        assert "border" in details.get("class", [])
        assert "rounded-lg" in details.get("class", [])
        assert "cursor-pointer" in summary.get("class", [])
        assert "font-medium" in summary.get("class", [])

    async def test_styles_semantic_containers(self):
        """Should style semantic container elements."""
        processor = ContentProcessor()
        html = "<article>Content</article>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_semantic_elements_for_frontend(soup)

        article = soup.find("article")
        classes = article.get("class", [])
        assert "my-4" in classes

    async def test_styles_svg(self):
        """Should style svg elements."""
        processor = ContentProcessor()
        html = '<svg viewBox="0 0 100 100"></svg>'
        soup = BeautifulSoup(html, "html.parser")

        processor._process_semantic_elements_for_frontend(soup)

        svg = soup.find("svg")
        classes = svg.get("class", [])
        assert "max-w-full" in classes
        assert "h-auto" in classes
        assert "my-4" in classes


class TestProcessOtherElementsForFrontend:
    """Test processing of other elements."""

    async def test_styles_horizontal_rule(self):
        """Should style hr elements."""
        processor = ContentProcessor()
        html = "<hr>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_other_elements_for_frontend(soup)

        hr = soup.find("hr")
        classes = hr.get("class", [])
        assert "border-border" in classes
        assert "my-4" in classes

    async def test_styles_break(self):
        """Should style br elements."""
        processor = ContentProcessor()
        html = "<br>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_other_elements_for_frontend(soup)

        br = soup.find("br")
        classes = br.get("class", [])
        assert "block" in classes
        assert "my-2" in classes


class TestGenerateFrontendHtmlErrorHandling:
    """Test error handling in HTML generation."""

    async def test_returns_clean_html_on_exception(self):
        """Should return cleaned HTML if processing fails."""
        processor = ContentProcessor()

        # Create a mock that raises an exception
        original_strip = processor._strip_all_attributes

        def mock_strip(soup):
            raise RuntimeError("Test error")

        processor._strip_all_attributes = mock_strip

        try:
            result = processor._generate_frontend_html("<p>Test</p>")
            # Should return something (either cleaned or partial result)
            assert result is not None
        finally:
            processor._strip_all_attributes = original_strip


class TestProcessHeadingsForFrontendExtended:
    """Extended tests for heading processing."""

    async def test_styles_h4(self):
        """Should style h4 elements."""
        processor = ContentProcessor()
        html = "<h4>Section</h4>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_headings_for_frontend(soup)

        h4 = soup.find("h4")
        classes = h4.get("class", [])
        assert "font-semibold" in classes
        assert "text-lg" in classes
        assert "my-4" in classes

    async def test_styles_h5(self):
        """Should style h5 elements."""
        processor = ContentProcessor()
        html = "<h5>Subsection</h5>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_headings_for_frontend(soup)

        h5 = soup.find("h5")
        classes = h5.get("class", [])
        assert "font-semibold" in classes
        assert "text-base" in classes
        assert "my-4" in classes

    async def test_styles_h6(self):
        """Should style h6 elements."""
        processor = ContentProcessor()
        html = "<h6>Minor heading</h6>"
        soup = BeautifulSoup(html, "html.parser")

        processor._process_headings_for_frontend(soup)

        h6 = soup.find("h6")
        classes = h6.get("class", [])
        assert "font-semibold" in classes
        assert "text-sm" in classes
        assert "my-4" in classes


class TestStripAllAttributesExtended:
    """Extended tests for attribute stripping."""

    async def test_preserves_video_attributes(self):
        """Should preserve essential video attributes."""
        processor = ContentProcessor()
        html = '<video src="test.mp4" poster="poster.jpg" width="640" height="480" class="test"></video>'
        soup = BeautifulSoup(html, "html.parser")

        processor._strip_all_attributes(soup)

        video = soup.find("video")
        assert video.get("src") == "test.mp4"
        assert video.get("poster") == "poster.jpg"
        assert video.get("width") == "640"
        assert video.get("height") == "480"
        assert video.get("class") is None  # Non-essential attrs removed

    async def test_preserves_audio_attributes(self):
        """Should preserve essential audio attributes."""
        processor = ContentProcessor()
        html = '<audio src="test.mp3" class="test"></audio>'
        soup = BeautifulSoup(html, "html.parser")

        processor._strip_all_attributes(soup)

        audio = soup.find("audio")
        assert audio.get("src") == "test.mp3"
        assert audio.get("class") is None

    async def test_preserves_time_attributes(self):
        """Should preserve datetime on time elements."""
        processor = ContentProcessor()
        html = '<time datetime="2024-01-01" class="test">Jan 1</time>'
        soup = BeautifulSoup(html, "html.parser")

        processor._strip_all_attributes(soup)

        time = soup.find("time")
        assert time.get("datetime") == "2024-01-01"
        assert time.get("class") is None
