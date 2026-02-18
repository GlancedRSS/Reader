"""Media extraction utilities for RSS feed content."""

from typing import Any
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from backend.infrastructure.feed.utils.constants import IMAGE_EXTENSIONS


class MediaExtractor:
    """Extracts media references from HTML content and RSS feed entries."""

    def __init__(self) -> None:
        """Initialize the media extractor with supported image extensions."""
        self.image_extensions = IMAGE_EXTENSIONS

    def extract_image_from_entry(self, entry: Any) -> str | None:
        """Extract image from RSS/ATOM entry metadata."""
        if hasattr(entry, "media_group") and entry.media_group:
            for group in entry.media_group:
                if isinstance(group, dict):
                    media_thumbnail = group.get("media_thumbnail")
                    if media_thumbnail and isinstance(media_thumbnail, list):
                        thumbnail = (
                            media_thumbnail[0] if media_thumbnail else {}
                        )
                        url = thumbnail.get("url") or thumbnail.get("href")
                        if url:
                            return str(url)

        if hasattr(entry, "media_content") and entry.media_content:
            for media in entry.media_content:
                if isinstance(media, dict):
                    media_type = media.get("type", "") or media.get(
                        "medium", ""
                    )
                    if media_type and ("image" in str(media_type).lower()):
                        return (
                            str(media.get("url")) if media.get("url") else None
                        )

        if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
            for thumbnail in entry.media_thumbnail:
                if isinstance(thumbnail, dict):
                    thumbnail_url = thumbnail.get("url") or thumbnail.get(
                        "href"
                    )
                    if thumbnail_url:
                        return str(thumbnail_url)

        if hasattr(entry, "thumbnail"):
            thumbnail = getattr(entry, "thumbnail", "")
            if thumbnail:
                if isinstance(thumbnail, dict):
                    url = thumbnail.get("url") or thumbnail.get("href")
                    return str(url) if url else None
                return str(thumbnail)

        if hasattr(entry, "enclosures") and entry.enclosures:
            for enclosure in entry.enclosures:
                if isinstance(enclosure, dict):
                    if enclosure.get("type", "").startswith("image/"):
                        url = enclosure.get("href") or enclosure.get("url")
                        return str(url) if url else None

        if hasattr(entry, "image"):
            image = getattr(entry, "image", "")
            if image:
                if isinstance(image, dict):
                    url = image.get("href") or image.get("url")
                    return str(url) if url else None
                return str(image)

        if hasattr(entry, "links") and entry.links:
            for link in entry.links:
                if isinstance(link, dict):
                    rel = link.get("rel", "")
                    link_type = link.get("type", "")
                    href = link.get("href", "")

                    if href and (
                        rel == "image"
                        or (
                            rel == "enclosure"
                            and str(link_type).startswith("image/")
                        )
                    ):
                        return str(href)

        return None

    def extract_image_from_summary_description(self, entry: Any) -> str | None:
        """Extract first image from RSS/ATOM summary and description fields."""
        if hasattr(entry, "summary") and entry.summary:
            summary_content = entry.summary
            if isinstance(summary_content, str) and summary_content.strip():
                img_url = self.extract_image_from_html(summary_content)
                if img_url:
                    return img_url

        if hasattr(entry, "description") and entry.description:
            description_content = entry.description
            if (
                isinstance(description_content, str)
                and description_content.strip()
            ):
                img_url = self.extract_image_from_html(description_content)
                if img_url:
                    return img_url

        return None

    def extract_image_from_html(self, html_content: str) -> str | None:
        """Extract first image from HTML content."""
        if not html_content:
            return None

        try:
            soup = BeautifulSoup(html_content, "html.parser")

            img_tag = soup.find("img")
            if img_tag and img_tag.get("src"):
                img_url = img_tag.get("src")
                if isinstance(img_url, str) and self._is_valid_image_url(
                    img_url
                ):
                    return img_url

            og_img = soup.find("meta", property="og:image")
            if og_img and og_img.get("content"):
                content = og_img.get("content")
                return str(content) if content else None

            return None

        except Exception as e:
            import structlog

            logger = structlog.get_logger()
            logger.warning("Error extracting image from HTML", error=str(e))
            return None

    def extract_metadata_from_entry(self, entry: Any) -> dict[str, Any]:
        """Extract platform-specific metadata from RSS/ATOM entry."""
        metadata: dict[str, Any] = {}

        if hasattr(entry, "enclosures") and entry.enclosures:
            for enclosure in entry.enclosures:
                if isinstance(enclosure, dict):
                    enc_type = enclosure.get("type", "")
                    if enc_type and "audio" in enc_type.lower():
                        metadata["podcast"] = {
                            "audio_url": enclosure.get("href"),
                            "type": enc_type,
                            "length": enclosure.get("length"),
                        }
                        break

        if hasattr(entry, "yt_videoid"):
            metadata["youtube"] = {
                "video_id": entry.yt_videoid,
            }
            if hasattr(entry, "yt_channelid"):
                metadata["youtube"]["channel_id"] = entry.yt_channelid

        if not hasattr(entry, "media_group") or not entry.media_group:
            return metadata

        for group in entry.media_group:
            if not isinstance(group, dict):
                continue

            media_content = group.get("media_content")
            if media_content and isinstance(media_content, list):
                for content in media_content:
                    if isinstance(content, dict):
                        medium = content.get("medium") or content.get(
                            "type", ""
                        )
                        if "video" in str(medium).lower():
                            if "duration" in content:
                                platform = metadata.get("youtube", {})
                                platform["duration"] = int(content["duration"])
                                if "youtube" not in metadata:
                                    metadata["youtube"] = platform
                            break

            media_community = group.get("media_community")
            if media_community and isinstance(media_community, dict):
                platform_key = "youtube"

                media_statistics = media_community.get("media_statistics")
                if media_statistics and isinstance(media_statistics, dict):
                    platform = metadata.get(platform_key, {})
                    if "views" in media_statistics:
                        platform["views"] = int(media_statistics["views"])
                    if platform_key not in metadata:
                        metadata[platform_key] = platform

                star_rating = media_community.get("media_starRating")
                if star_rating and isinstance(star_rating, dict):
                    platform = metadata.get(platform_key, {})
                    if "average" in star_rating:
                        platform["rating"] = float(star_rating["average"])
                    if "count" in star_rating:
                        platform["rating_count"] = int(star_rating["count"])
                    if platform_key not in metadata:
                        metadata[platform_key] = platform

            media_thumbnail = group.get("media_thumbnail")
            if (
                media_thumbnail
                and isinstance(media_thumbnail, list)
                and media_thumbnail
            ):
                thumb = media_thumbnail[0]
                if isinstance(thumb, dict):
                    existing_platform = next(
                        (k for k in metadata if k in ("youtube", "vimeo")), None
                    )
                    if existing_platform:
                        platform = metadata[existing_platform]
                        if "width" in thumb:
                            platform["thumbnail_width"] = int(thumb["width"])
                        if "height" in thumb:
                            platform["thumbnail_height"] = int(thumb["height"])

        return metadata

    def _is_valid_image_url(self, url: str) -> bool:
        """Check if URL is a valid image."""
        if not url or not url.startswith(("http://", "https://")):
            return False

        parsed = urlparse(url.lower())
        if any(parsed.path.endswith(ext) for ext in self.image_extensions):
            return True

        return False
