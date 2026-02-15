# type: ignore
"""Frontend HTML processor for article content display."""

from bs4 import BeautifulSoup

from backend.infrastructure.parsers import HTMLCleaner


class ContentProcessor:
    """Content processor for generating frontend-ready HTML with Tailwind CSS styling."""

    def __init__(self):
        """Initialize the content processor with HTML cleaner."""
        self.html_cleaner = HTMLCleaner()

    def _generate_frontend_html(self, html_content: str) -> str:
        """Generate frontend-compatible HTML with Tailwind classes.

        Processes raw HTML to add responsive Tailwind CSS classes, lazy loading
        for images, and proper accessibility attributes.

        Args:
            html_content: Raw HTML content from RSS feed.

        Returns:
            Frontend-ready HTML string with proper classes and attributes.

        """
        if not html_content:
            return ""

        clean_html = self.html_cleaner.clean_html(html_content)

        if not clean_html:
            return ""

        try:
            soup = BeautifulSoup(clean_html, "html.parser")

            self._strip_all_attributes(soup)
            self._remove_empty_and_unnecessary_elements(soup)

            self._process_images_for_frontend(soup)
            self._process_links_for_frontend(soup)
            self._process_headings_for_frontend(soup)
            self._process_paragraphs_for_frontend(soup)
            self._process_text_formatting_for_frontend(soup)
            self._process_lists_for_frontend(soup)
            self._process_code_blocks_for_frontend(soup)
            self._process_blockquotes_for_frontend(soup)
            self._process_tables_for_frontend(soup)
            self._process_videos_for_frontend(soup)
            self._process_audio_for_frontend(soup)
            self._process_iframes_for_frontend(soup)
            self._process_semantic_elements_for_frontend(soup)
            self._process_other_elements_for_frontend(soup)

            return str(soup)

        except Exception as e:
            import structlog

            logger = structlog.get_logger()
            logger.warning("Error generating frontend HTML", error=str(e))
            return clean_html

    def _process_images_for_frontend(self, soup: BeautifulSoup) -> None:
        """Process images with Tailwind classes matching frontend styling.

        Args:
            soup: BeautifulSoup object containing parsed HTML.

        """
        for img in soup.find_all("img"):
            existing_classes = img.get("class", [])
            if isinstance(existing_classes, str):
                existing_classes = [existing_classes]

            img["class"] = [
                *existing_classes,
                "max-w-full",
                "h-auto",
                "rounded-xl",
                "shadow-sm",
                "mx-auto",
                "my-4",
            ]

            if not img.get("loading"):
                img["loading"] = "lazy"

            if not img.get("alt"):
                img["alt"] = ""

    def _process_links_for_frontend(self, soup: BeautifulSoup) -> None:
        """Process links with Tailwind classes and security attributes.

        Args:
            soup: BeautifulSoup object containing parsed HTML.

        """
        for link in soup.find_all("a"):
            href = link.get("href", "")

            existing_classes = link.get("class", [])
            if isinstance(existing_classes, str):
                existing_classes = [existing_classes]

            link["class"] = [
                *existing_classes,
                "text-primary",
                "hover:underline",
            ]

            if href.startswith(("http://", "https://")):
                link["target"] = "_blank"
                link["rel"] = "noopener noreferrer"

    def _process_headings_for_frontend(self, soup: BeautifulSoup) -> None:
        """Process headings with proper typography classes.

        Args:
            soup: BeautifulSoup object containing parsed HTML.

        """
        heading_classes = {
            "h1": ["font-semibold", "my-4", "text-3xl"],
            "h2": ["font-semibold", "my-4", "text-2xl"],
            "h3": ["font-semibold", "my-4", "text-xl"],
            "h4": ["font-semibold", "my-4", "text-lg"],
            "h5": ["font-semibold", "my-4", "text-base"],
            "h6": ["font-semibold", "my-4", "text-sm"],
        }

        for tag_name, classes in heading_classes.items():
            for heading in soup.find_all(tag_name):
                existing_classes = heading.get("class", [])
                if isinstance(existing_classes, str):
                    existing_classes = [existing_classes]

                heading["class"] = existing_classes + classes

    def _process_paragraphs_for_frontend(self, soup: BeautifulSoup) -> None:
        """Process paragraphs with proper spacing.

        Args:
            soup: BeautifulSoup object containing parsed HTML.

        """
        for p in soup.find_all("p"):
            existing_classes = p.get("class", [])
            if isinstance(existing_classes, str):
                existing_classes = [existing_classes]

            p["class"] = [*existing_classes, "my-4"]

    def _process_lists_for_frontend(self, soup: BeautifulSoup) -> None:
        """Process lists with proper styling.

        Args:
            soup: BeautifulSoup object containing parsed HTML.

        """
        for ul in soup.find_all("ul"):
            existing_classes = ul.get("class", [])
            if isinstance(existing_classes, str):
                existing_classes = [existing_classes]

            ul["class"] = [
                *existing_classes,
                "my-4",
                "pl-6",
                "space-y-2",
                "list-disc",
                "list-outside",
            ]

        for ol in soup.find_all("ol"):
            existing_classes = ol.get("class", [])
            if isinstance(existing_classes, str):
                existing_classes = [existing_classes]

            ol["class"] = [
                *existing_classes,
                "my-4",
                "pl-6",
                "space-y-2",
                "list-decimal",
                "list-outside",
            ]

        for li in soup.find_all("li"):
            existing_classes = li.get("class", [])
            if isinstance(existing_classes, str):
                existing_classes = [existing_classes]

            li["class"] = [*existing_classes, "my-1"]

    def _process_code_blocks_for_frontend(self, soup: BeautifulSoup) -> None:
        """Process code blocks with syntax highlighting appearance.

        Args:
            soup: BeautifulSoup object containing parsed HTML.

        """
        for code in soup.find_all("code"):
            parent = code.parent
            if parent and parent.name != "pre":
                existing_classes = code.get("class", [])
                if isinstance(existing_classes, str):
                    existing_classes = [existing_classes]

                code["class"] = [
                    *existing_classes,
                    "bg-muted",
                    "px-1",
                    "py-0.5",
                    "rounded",
                    "text-sm",
                    "font-mono",
                ]

        for pre in soup.find_all("pre"):
            existing_classes = pre.get("class", [])
            if isinstance(existing_classes, str):
                existing_classes = [existing_classes]

            pre["class"] = [
                *existing_classes,
                "bg-muted",
                "p-4",
                "rounded-lg",
                "overflow-x-auto",
                "my-4",
            ]

    def _process_blockquotes_for_frontend(self, soup: BeautifulSoup) -> None:
        """Process blockquotes with proper styling.

        Args:
            soup: BeautifulSoup object containing parsed HTML.

        """
        for blockquote in soup.find_all("blockquote"):
            existing_classes = blockquote.get("class", [])
            if isinstance(existing_classes, str):
                existing_classes = [existing_classes]

            blockquote["class"] = [
                *existing_classes,
                "border",
                "border-border/80",
                "bg-muted",
                "rounded-lg",
                "px-4",
                "my-4",
            ]

    def _process_tables_for_frontend(self, soup: BeautifulSoup) -> None:
        """Process tables with responsive styling.

        Args:
            soup: BeautifulSoup object containing parsed HTML.

        """
        for table in soup.find_all("table"):
            existing_classes = table.get("class", [])
            if isinstance(existing_classes, str):
                existing_classes = [existing_classes]

            table["class"] = [
                *existing_classes,
                "min-w-full",
                "border-collapse",
                "border",
                "border-border",
            ]

            wrapper = soup.new_tag("div")
            wrapper["class"] = "overflow-x-auto my-4"
            table.wrap(wrapper)

        for th in soup.find_all("th"):
            existing_classes = th.get("class", [])
            if isinstance(existing_classes, str):
                existing_classes = [existing_classes]

            th["class"] = [
                *existing_classes,
                "border",
                "border-border",
                "px-4",
                "py-2",
                "text-left",
                "font-medium",
            ]

        for td in soup.find_all("td"):
            existing_classes = td.get("class", [])
            if isinstance(existing_classes, str):
                existing_classes = [existing_classes]

            td["class"] = [
                *existing_classes,
                "border",
                "border-border",
                "px-4",
                "py-2",
            ]

    def _process_videos_for_frontend(self, soup: BeautifulSoup) -> None:
        """Process videos with responsive styling.

        Args:
            soup: BeautifulSoup object containing parsed HTML.

        """
        for video in soup.find_all("video"):
            existing_classes = video.get("class", [])
            if isinstance(existing_classes, str):
                existing_classes = [existing_classes]

            video["class"] = [
                *existing_classes,
                "w-full",
                "max-w-2xl",
                "rounded-lg",
                "shadow-lg",
                "my-4",
            ]

            if not video.get("controls"):
                video["controls"] = ""

    def _process_iframes_for_frontend(self, soup: BeautifulSoup) -> None:
        """Process iframe embeds with responsive sizing.

        Wraps iframes in divs with appropriate sizing classes based on the
        iframe source (video platforms get aspect ratio, audio gets fixed height).

        Args:
            soup: BeautifulSoup object containing parsed HTML.

        """
        for iframe in soup.find_all("iframe"):
            src = iframe.get("src", "")
            if not src:
                continue

            if iframe.get("style") == "":
                del iframe["style"]

            import re

            is_youtube = bool(re.search(r"youtube\.com|youtu\.be", src))
            is_vimeo = bool(re.search(r"vimeo\.com", src))
            is_spotify = bool(re.search(r"spotify\.com/embed", src))
            is_apple_music = bool(re.search(r"embed\.music\.apple\.com", src))
            is_soundcloud = bool(re.search(r"soundcloud\.com/player", src))

            if is_youtube or is_vimeo:
                wrapper = soup.new_tag("div")
                wrapper["class"] = (
                    "my-6 aspect-video w-full overflow-hidden rounded-xl"
                )
                iframe["loading"] = "lazy"
                iframe["class"] = "h-full w-full border-0"
                iframe.wrap(wrapper)
            elif is_spotify:
                wrapper = soup.new_tag("div")
                wrapper["class"] = (
                    "my-6 w-full h-[352px] overflow-hidden rounded-xl"
                )
                iframe["loading"] = "lazy"
                iframe["class"] = "h-full w-full border-0"
                iframe.wrap(wrapper)
            elif is_apple_music:
                wrapper = soup.new_tag("div")
                wrapper["class"] = (
                    "my-6 w-full h-[300px] overflow-hidden rounded-xl"
                )
                iframe["loading"] = "lazy"
                iframe["class"] = "h-full w-full border-0"
                iframe.wrap(wrapper)
            elif is_soundcloud:
                wrapper = soup.new_tag("div")
                wrapper["class"] = (
                    "my-6 w-full h-[166px] overflow-hidden rounded-xl"
                )
                iframe["loading"] = "lazy"
                iframe["class"] = "h-full w-full border-0"
                iframe.wrap(wrapper)
            else:
                wrapper = soup.new_tag("div")
                wrapper["class"] = (
                    "my-6 w-full h-[400px] overflow-hidden rounded-xl"
                )
                iframe["loading"] = "lazy"
                iframe["class"] = "h-full w-full border-0"
                iframe.wrap(wrapper)

    def _process_audio_for_frontend(self, soup: BeautifulSoup) -> None:
        """Process audio elements with styling.

        Args:
            soup: BeautifulSoup object containing parsed HTML.

        """
        for audio in soup.find_all("audio"):
            existing_classes = audio.get("class", [])
            if isinstance(existing_classes, str):
                existing_classes = [existing_classes]

            audio["class"] = [*existing_classes, "w-full", "max-w-md", "my-4"]

            if not audio.get("controls"):
                audio["controls"] = ""

    def _strip_all_attributes(self, soup: BeautifulSoup) -> None:
        """Strip all existing attributes to ensure clean styling.

        Preserves essential attributes for functionality (src, href, alt, etc).

        Args:
            soup: BeautifulSoup object containing parsed HTML.

        """
        preserve_attrs = {
            "img": ["src", "alt", "width", "height"],
            "a": ["href"],
            "video": ["src", "poster", "width", "height"],
            "audio": ["src"],
            "source": ["src", "type"],
            "track": ["src", "kind", "srclang", "label"],
            "iframe": [
                "src",
                "width",
                "height",
                "allowfullscreen",
                "allow",
                "frameborder",
                "scrolling",
                "referrerpolicy",
            ],
            "embed": ["src", "width", "height"],
            "object": ["data", "width", "height"],
            "blockquote": ["cite", "class", "align"],
            "time": ["datetime"],
        }

        for element in soup.find_all():
            tag_name = element.name
            attrs_to_keep = preserve_attrs.get(tag_name, [])

            new_attrs = {}
            for attr in attrs_to_keep:
                if element.get(attr):
                    new_attrs[attr] = element[attr]

            element.attrs = new_attrs

    def _remove_empty_and_unnecessary_elements(
        self, soup: BeautifulSoup
    ) -> None:
        """Remove empty elements, unnecessary wrappers, and clutter.

        Args:
            soup: BeautifulSoup object containing parsed HTML.

        """
        empty_meaningless_tags = [
            "p",
            "div",
            "span",
            "section",
            "article",
            "aside",
            "header",
            "footer",
            "nav",
            "main",
            "figure",
            "figcaption",
            "details",
            "summary",
        ]

        for tag_name in empty_meaningless_tags:
            for element in soup.find_all(tag_name):
                if not self._has_meaningful_content(element):
                    element.decompose()

        for wrapper in soup.find_all(["div", "span"]):
            if (
                not wrapper.get("class")
                and not wrapper.get("id")
                and not wrapper.get("style")
            ):
                children = list(wrapper.children)
                if len(children) == 1 and not isinstance(children[0], str):
                    child = children[0]
                    if child.name:
                        wrapper.replace_with(child)

        for br in soup.find_all("br"):
            next_sibling = br.next_sibling
            if next_sibling and next_sibling.name == "br":
                br.decompose()

        from bs4 import Comment

        for comment in soup.find_all(
            string=lambda text: isinstance(text, Comment)
        ):
            comment.extract()

    def _has_meaningful_content(self, element) -> bool:
        """Check if an element has meaningful content worth preserving.

        Args:
            element: BeautifulSoup element to check.

        Returns:
            True if element has text content or meaningful child elements.

        """
        if not element:
            return False

        text_content = element.get_text(strip=True)
        if text_content:
            return True

        meaningful_tags = {
            "img",
            "video",
            "audio",
            "iframe",
            "embed",
            "object",
            "canvas",
            "svg",
        }
        for child in element.find_all():
            if child.name in meaningful_tags:
                if child.name == "img" and child.get("src"):
                    return True
                if child.name == "video" and child.get("src"):
                    return True
                if child.name == "audio" and child.get("src"):
                    return True
                if child.name in {"iframe", "embed", "object"} and child.get(
                    "src"
                ):
                    return True
                if child.name == "svg":
                    return True

        return False

    def _process_text_formatting_for_frontend(
        self, soup: BeautifulSoup
    ) -> None:
        """Process text formatting elements.

        Args:
            soup: BeautifulSoup object containing parsed HTML.

        """
        for sup in soup.find_all("sup"):
            sup["class"] = ["text-sm"]

        for sub in soup.find_all("sub"):
            sub["class"] = ["text-sm"]

    def _process_semantic_elements_for_frontend(
        self, soup: BeautifulSoup
    ) -> None:
        """Process HTML5 semantic and structural elements.

        Args:
            soup: BeautifulSoup object containing parsed HTML.

        """
        for mark in soup.find_all("mark"):
            mark["class"] = [
                "bg-yellow-200/50",
                "dark:bg-yellow-900/30",
                "px-1",
            ]

        for cite in soup.find_all("cite"):
            cite["class"] = ["italic"]

        for quote in soup.find_all("q"):
            quote["class"] = ["italic"]

        for abbr in soup.find_all("abbr"):
            abbr["class"] = [
                "border-b",
                "border-dotted",
                "border-muted-foreground",
                "cursor-help",
            ]

        for address in soup.find_all("address"):
            address["class"] = ["not-italic", "my-4", "text-muted-foreground"]

        for small in soup.find_all("small"):
            small["class"] = ["text-sm", "text-muted-foreground"]

        for time in soup.find_all("time"):
            time["class"] = ["text-muted-foreground", "text-sm"]

        for dl in soup.find_all("dl"):
            dl["class"] = ["my-4"]

        for dt in soup.find_all("dt"):
            dt["class"] = ["font-medium", "text-foreground", "mb-1"]

        for dd in soup.find_all("dd"):
            dd["class"] = ["ml-4", "mb-2", "text-muted-foreground"]

        for figure in soup.find_all("figure"):
            figure["class"] = ["my-4"]

        for figcaption in soup.find_all("figcaption"):
            figcaption["class"] = [
                "text-sm",
                "text-muted-foreground",
                "mt-2",
                "text-center",
            ]

        for details in soup.find_all("details"):
            details["class"] = [
                "my-4",
                "border",
                "border-border",
                "rounded-lg",
                "p-4",
            ]

        for summary in soup.find_all("summary"):
            summary["class"] = [
                "cursor-pointer",
                "font-medium",
                "text-foreground",
                "mb-2",
            ]

        semantic_containers = [
            "article",
            "section",
            "nav",
            "aside",
            "header",
            "footer",
            "main",
        ]
        for container in soup.find_all(semantic_containers):
            existing_classes = container.get("class", [])
            if isinstance(existing_classes, str):
                existing_classes = [existing_classes]

            container["class"] = [*existing_classes, "my-4"]

        for svg in soup.find_all("svg"):
            svg["class"] = ["max-w-full", "h-auto", "my-4"]

    def _process_other_elements_for_frontend(self, soup: BeautifulSoup) -> None:
        """Process remaining elements like horizontal rules and breaks.

        Args:
            soup: BeautifulSoup object containing parsed HTML.

        """
        for hr in soup.find_all("hr"):
            hr["class"] = ["border-border", "my-4"]

        for br in soup.find_all("br"):
            br["class"] = ["block", "my-2"]
