"""OPML job handlers."""

from datetime import UTC, datetime
from uuid import UUID
from xml.etree import ElementTree as ET

from sqlalchemy import select
from structlog import get_logger

from backend.core.database import AsyncSessionLocal
from backend.domain import OPML_FILE_EXPIRY_HOURS
from backend.domain.opml import OpmlParser
from backend.infrastructure.feed.processing.feed_processor import (
    FeedProcessor,
)
from backend.infrastructure.jobs.base import BaseJobHandler
from backend.infrastructure.notifications.notifications import (
    publish_notification,
)
from backend.infrastructure.repositories import (
    FeedRepository,
    UserFeedRepository,
)
from backend.infrastructure.storage.local import LocalOpmlStorage
from backend.schemas.feeds import DiscoveryFeedCreateRequest
from backend.schemas.workers import (
    OpmlExportJobRequest,
    OpmlExportJobResponse,
    OpmlImportJobRequest,
    OpmlImportJobResponse,
)

logger = get_logger(__name__)


class OpmlImportJobHandler(
    BaseJobHandler[OpmlImportJobRequest, OpmlImportJobResponse]
):
    """Handler for OPML import job."""

    MAX_FOLDER_DEPTH = 9

    async def execute(
        self, request: OpmlImportJobRequest
    ) -> OpmlImportJobResponse:
        """Execute the OPML import job."""
        logger.info(
            "Starting OPML import",
            job_id=request.job_id,
            user_id=request.user_id,
            filename=request.filename,
            storage_key=request.storage_key,
        )

        async with AsyncSessionLocal() as db:
            from backend.models import Feed, UserFeed

            stmt = (
                select(Feed.canonical_url)
                .join(UserFeed, UserFeed.feed_id == Feed.id)
                .where(UserFeed.user_id == UUID(request.user_id))
            )
            result = await db.execute(stmt)
            existing_urls = set(row[0] for row in result.all())

        storage = LocalOpmlStorage()
        try:
            content_bytes = await storage.download_file(request.storage_key)
        except FileNotFoundError as err:
            logger.exception(
                "OPML file not found in local storage",
                storage_key=request.storage_key,
            )
            raise ValueError(
                f"OPML file not found: {request.storage_key}"
            ) from err

        parse_result = OpmlParser.validate_and_parse(
            file_content=content_bytes,
            filename=request.filename,
            existing_urls=existing_urls,
        )

        if not parse_result.is_valid:
            error_msg = "; ".join(parse_result.errors)
            logger.error(
                "OPML validation failed",
                errors=parse_result.errors,
            )
            raise ValueError(f"Invalid OPML file: {error_msg}")

        total_feeds = parse_result.total_feeds
        valid_feeds = parse_result.feeds
        invalid_urls = parse_result.invalid_urls
        duplicate_urls = parse_result.duplicate_urls

        logger.info(
            "OPML parsed",
            total_feeds=total_feeds,
            valid_feeds=len(valid_feeds),
            invalid_urls=len(invalid_urls),
            duplicate_urls=len(duplicate_urls),
            encoding=parse_result.encoding,
        )

        imported_feeds = []
        failed_feeds = []
        duplicate_count = len(duplicate_urls)

        for invalid in invalid_urls:
            failed_feeds.append(
                {
                    "title": invalid.get("title", "Unknown"),
                    "url": invalid.get("url", ""),
                    "error": invalid.get("error", "Unknown error"),
                }
            )

        for i, feed in enumerate(valid_feeds):
            feed_url = feed.url
            feed_title = feed.title

            folder_id = await self._resolve_or_create_folder(
                UUID(request.user_id),
                feed.folder_path,
                UUID(request.folder_id) if request.folder_id else None,
            )

            logger.debug(
                "Importing feed",
                feed_url=feed_url,
                feed_title=feed_title,
                folder_path=feed.folder_path,
                folder_id=str(folder_id) if folder_id else None,
            )

            try:
                status = await self._import_feed(
                    feed_url=feed_url,
                    feed_title=feed_title,
                    user_id=UUID(request.user_id),
                    import_id=UUID(request.import_id),
                    folder_id=folder_id,
                )

                if status == "success":
                    imported_feeds.append(
                        {
                            "title": feed_title or "Unknown",
                            "url": feed_url,
                        }
                    )

            except Exception as e:
                logger.error(
                    "Failed to import feed",
                    feed_url=feed_url,
                    feed_title=feed_title,
                    error=str(e),
                    exc_info=True,
                )
                failed_feeds.append(
                    {
                        "title": feed_title or "Unknown",
                        "url": feed_url,
                        "error": str(e),
                    }
                )

            if (i + 1) % 10 == 0 or i == len(valid_feeds) - 1:
                await self._send_progress_update(
                    UUID(request.user_id),
                    UUID(request.import_id),
                    i + 1,
                    len(valid_feeds),
                )
                logger.info(
                    "OPML import progress",
                    job_id=request.job_id,
                    progress=f"{i + 1}/{len(valid_feeds)}",
                )

        logger.info(
            "OPML import completed",
            job_id=request.job_id,
            total_feeds=total_feeds,
            imported_feeds=len(imported_feeds),
            failed_feeds=len(failed_feeds),
            duplicate_feeds=duplicate_count,
        )

        status = (
            "completed" if len(failed_feeds) == 0 else "completed_with_errors"
        )

        async with AsyncSessionLocal() as db:
            from backend.infrastructure.repositories.opml import OpmlRepository

            repo = OpmlRepository(db)
            await repo.update_import_status(
                import_id=UUID(request.import_id),
                status=status,
                total_feeds=total_feeds,
                imported_feeds=len(imported_feeds),
                failed_feeds=len(failed_feeds),
                duplicate_feeds=duplicate_count,
                failed_feeds_log=failed_feeds,
            )
            opml_import = await repo.get_import_by_id(UUID(request.import_id))
            if opml_import:
                opml_import.completed_at = datetime.now(UTC)
            await db.commit()

        await publish_notification(
            user_id=UUID(request.user_id),
            event_type="opml_import_complete",
            data={
                "import_id": str(request.import_id),
                "total_feeds": total_feeds,
                "imported_feeds": len(imported_feeds),
                "failed_feeds": len(failed_feeds),
                "duplicate_feeds": duplicate_count,
            },
        )

        return OpmlImportJobResponse(
            job_id=request.job_id,
            status="completed"
            if len(failed_feeds) == 0
            else "completed_with_errors",
            message=f"Imported {len(imported_feeds)} feeds, {len(failed_feeds)} failed, {duplicate_count} duplicates",
            total_feeds=total_feeds,
            imported_feeds=len(imported_feeds),
            failed_feeds=len(failed_feeds),
            duplicate_feeds=duplicate_count,
        )

    async def _import_feed(
        self,
        feed_url: str,
        feed_title: str | None,
        user_id: UUID,
        import_id: UUID,
        folder_id: UUID | None,
    ) -> str:
        """Import a single feed using feed processor and user feed repository."""
        logger.info(
            "Importing feed",
            feed_url=feed_url,
            folder_id=str(folder_id) if folder_id else None,
        )

        async with AsyncSessionLocal() as db:
            feed_repo = FeedRepository(db)
            user_feed_repo = UserFeedRepository(db)
            feed_processor = FeedProcessor(db)

            feed = await feed_repo.get_feed_by_url(feed_url)

            if not feed:
                feed_request = DiscoveryFeedCreateRequest(
                    url=feed_url, title=None
                )
                feed = await feed_processor.create_feed(feed_request)

            from backend.models.user_feed import UserFeed

            existing_sub = await db.execute(
                select(UserFeed).where(
                    UserFeed.user_id == user_id,
                    UserFeed.feed_id == feed.id,
                )
            )
            existing = existing_sub.scalar_one_or_none()

            if existing:
                existing.import_id = import_id
                existing.folder_id = folder_id
                await db.commit()
                return "exists"

            subscription = await user_feed_repo.create_user_feed(
                user_id=user_id,
                feed_id=feed.id,
                title=feed.title or feed_url,
                folder_id=folder_id,
            )

            if feed.latest_articles:
                await user_feed_repo.bulk_upsert_user_article_states(
                    user_id,
                    feed.latest_articles,
                )

                from backend.application.feed.feed import FeedApplication

                feed_app = FeedApplication(db)
                await feed_app._backfill_tags_for_articles(
                    user_id, feed.latest_articles
                )

            subscription.import_id = import_id
            await db.commit()

            return "success"

    async def _resolve_or_create_folder(
        self,
        user_id: UUID,
        folder_path: list[str],
        default_parent_id: UUID | None,
    ) -> UUID | None:
        """Resolve or create folders from path."""
        if not folder_path:
            return default_parent_id

        async with AsyncSessionLocal() as db:
            from backend.models.user_folder import UserFolder

            current_parent_id = default_parent_id

            for folder_name in folder_path:
                stmt = select(UserFolder).where(
                    UserFolder.user_id == user_id,
                    UserFolder.parent_id == current_parent_id,
                    UserFolder.name == folder_name[:16],
                )
                result = await db.execute(stmt)
                folder = result.scalar_one_or_none()

                if not folder:
                    folder = UserFolder(
                        user_id=user_id,
                        name=folder_name[:16],
                        parent_id=current_parent_id,
                    )
                    db.add(folder)
                    await db.flush()
                    await db.refresh(folder)

                current_parent_id = folder.id

            await db.commit()
            return current_parent_id

    async def _send_progress_update(
        self,
        user_id: UUID,
        import_id: UUID,
        current: int,
        total: int,
    ) -> None:
        """Send SSE progress update via Redis pub/sub."""
        from backend.infrastructure.notifications.notifications import (
            publish_notification,
        )

        await publish_notification(
            user_id=user_id,
            event_type="opml_import_progress",
            data={
                "import_id": str(import_id),
                "current": current,
                "total": total,
                "percentage": int((current / total) * 100) if total > 0 else 0,
            },
        )


class OpmlExportJobHandler(
    BaseJobHandler[OpmlExportJobRequest, OpmlExportJobResponse]
):
    """Handler for OPML export job."""

    async def execute(
        self, request: OpmlExportJobRequest
    ) -> OpmlExportJobResponse:
        """Execute the OPML export job."""
        logger.info(
            "Starting OPML export",
            job_id=request.job_id,
            user_id=request.user_id,
        )

        start_time = datetime.now(UTC)

        opml_content = None
        total_feeds = 0
        filename = None
        storage_key = None
        download_url = None
        file_size = 0

        try:
            async with AsyncSessionLocal() as db:
                from backend.models import Feed, User, UserFeed
                from backend.models.user_folder import UserFolder

                user_result = await db.execute(
                    select(User).where(User.id == UUID(request.user_id))
                )
                user = user_result.scalar_one_or_none()

                if not user:
                    raise ValueError("User not found")

                stmt = (
                    select(UserFeed, Feed)
                    .join(Feed, UserFeed.feed_id == Feed.id)
                    .where(UserFeed.user_id == user.id)
                )

                if request.folder_id:
                    stmt = stmt.where(
                        UserFeed.folder_id == UUID(request.folder_id)
                    )

                result = await db.execute(stmt)
                subscriptions = result.all()

                total_feeds = len(subscriptions)

                opml = ET.Element("opml", version="2.0")

                head = ET.SubElement(opml, "head")
                title = ET.SubElement(head, "title")
                title.text = (
                    f"{user.first_name or user.username}'s Glanced Reader Feeds"
                )

                date_created = ET.SubElement(head, "dateCreated")
                date_created.text = datetime.now(UTC).isoformat()

                body = ET.SubElement(opml, "body")

                folders: dict[UUID | None, list[tuple[UserFeed, Feed]]] = {}
                root_feeds: list[tuple[UserFeed, Feed]] = []

                for sub, feed in subscriptions:
                    if sub.folder_id:
                        if sub.folder_id not in folders:
                            folders[sub.folder_id] = []
                        folders[sub.folder_id].append((sub, feed))
                    else:
                        root_feeds.append((sub, feed))

                for sub, feed in root_feeds:
                    ET.SubElement(
                        body,
                        "outline",
                        attrib={
                            "text": sub.title or feed.title or "Untitled",
                            "title": sub.title or feed.title or "Untitled",
                            "type": "rss",
                            "xmlUrl": feed.canonical_url or "",
                        },
                    )

                if folders:
                    folder_ids = list(folders.keys())
                    folder_result = await db.execute(
                        select(UserFolder).where(UserFolder.id.in_(folder_ids))
                    )
                    folder_names = {
                        f.id: f.name for f in folder_result.scalars()
                    }

                    for folder_id, subs_feeds in folders.items():
                        folder_name = (
                            folder_names.get(folder_id, f"Folder {folder_id}")
                            if folder_id
                            else "Root"
                        )
                        folder_outline = ET.SubElement(
                            body,
                            "outline",
                            attrib={"text": folder_name, "title": folder_name},
                        )

                        for sub, feed in subs_feeds:
                            ET.SubElement(
                                folder_outline,
                                "outline",
                                attrib={
                                    "text": sub.title
                                    or feed.title
                                    or "Untitled",
                                    "title": sub.title
                                    or feed.title
                                    or "Untitled",
                                    "type": "rss",
                                    "xmlUrl": feed.canonical_url or "",
                                },
                            )

                ET.indent(opml, space="    ")
                opml_content = ET.tostring(opml, encoding="unicode")

            storage = LocalOpmlStorage()
            date_str = datetime.now(UTC).strftime("%Y%m%d")
            record_id_short = request.export_id[:8]
            filename = (
                f"glanced-reader-export-{date_str}-{record_id_short}.opml"
            )

            storage_key = storage.generate_storage_key(
                f"users/{request.user_id}/exports", filename
            )

            opml_bytes = opml_content.encode("utf-8")
            await storage.upload_file(
                storage_key,
                opml_bytes,
                content_type="application/xml",
                expires_in_hours=OPML_FILE_EXPIRY_HOURS,
            )

            file_size = len(opml_bytes)
            processing_time_ms = int(
                (datetime.now(UTC) - start_time).total_seconds() * 1000
            )
            download_url = storage.generate_download_url(
                storage_key, expiration_seconds=OPML_FILE_EXPIRY_HOURS * 3600
            )

            logger.info(
                "OPML export completed",
                job_id=request.job_id,
                total_feeds=total_feeds,
                file_size=file_size,
                filename=filename,
                storage_key=storage_key,
                processing_time_ms=processing_time_ms,
            )

            await publish_notification(
                user_id=UUID(request.user_id),
                event_type="opml_export_complete",
                data={
                    "export_id": str(request.export_id),
                    "total_feeds": total_feeds,
                    "download_url": download_url,
                    "filename": filename,
                },
            )
            return OpmlExportJobResponse(
                job_id=request.job_id,
                status="success",
                message=f"Exported {total_feeds} feeds",
                total_feeds=total_feeds,
                file_size=file_size,
                download_url=download_url,
                filename=filename,
            )

        except Exception as e:
            processing_time_ms = int(
                (datetime.now(UTC) - start_time).total_seconds() * 1000
            )
            logger.error(
                "OPML export failed",
                job_id=request.job_id,
                user_id=request.user_id,
                error=str(e),
                exc_info=True,
            )
            raise
