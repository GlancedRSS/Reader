"""Application service for OPML import/export operations."""

import uuid
from uuid import UUID

import structlog
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.opml import OpmlValidation
from backend.infrastructure.external.arq_client import ArqClient
from backend.infrastructure.external.local_storage import LocalStorageClient
from backend.infrastructure.repositories import (
    FolderRepository,
    OpmlRepository,
    UserFeedRepository,
    UserTagRepository,
)
from backend.models import UserFeed
from backend.schemas.core import ResponseMessage
from backend.schemas.domain import (
    OpmlExportRequest,
    OpmlImport,
    OpmlOperationResponse,
    OpmlUploadResponse,
)

logger = structlog.get_logger()


class OpmlApplication:
    """Application service for OPML import/export operations."""

    def __init__(self, db: AsyncSession):
        """Initialize the OPML application with database session."""
        self.db = db
        self.repository = OpmlRepository(db)
        self.folder_repo = FolderRepository(db)
        self.user_feed_repo = UserFeedRepository(db)
        self.tag_repo = UserTagRepository(db)

    def _get_storage_client(self) -> LocalStorageClient:
        """Get local storage client."""
        return LocalStorageClient()

    async def validate_folder_ownership(
        self, folder_id: UUID, user_id: UUID
    ) -> bool:
        """Validate that the user owns the folder."""
        folder = await self.folder_repo.get_folder_by_id_and_user(
            folder_id, user_id
        )
        return folder is not None

    async def export_opml(
        self, request: OpmlExportRequest, user_id: UUID
    ) -> ResponseMessage:
        """Export user's feeds as OPML using background processing via Arq."""
        job_id = uuid.uuid4()

        client = ArqClient()

        try:
            await client.enqueue_job(
                function_name="opml_export",
                job_name="opml_export",
                job_id=str(job_id),
                user_id=str(user_id),
                export_id=str(job_id),
                folder_id=str(request.folder_id) if request.folder_id else None,
            )
            logger.info(
                "OPML export job enqueued with Arq",
                user_id=user_id,
                export_id=str(job_id),
            )
        except Exception as e:
            logger.exception(
                "Failed to enqueue OPML export job with Arq",
                user_id=user_id,
                export_id=str(job_id),
                error=str(e),
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to queue export job: {e}",
            ) from e

        return ResponseMessage(
            message="OPML export queued successfully. You will be notified when ready."
        )

    async def upload_opml_file(
        self, file_content: bytes, filename: str, user_id: UUID
    ) -> OpmlUploadResponse:
        """Upload and validate OPML file to local storage."""
        file_content_str, file_size, _encoding = (
            OpmlValidation.validate_opml_file_metadata(file_content, filename)
        )

        opml_import = await self.repository.create_import_record(
            user_id=user_id,
            filename=filename,
            status="pending",
            storage_key=None,
        )
        import_id: UUID = opml_import.id

        storage_client = self._get_storage_client()
        original_name = filename.removesuffix(".opml")
        unique_filename = f"{original_name}-{import_id}.opml"
        storage_key = storage_client.generate_storage_key(
            f"users/{user_id}/imports", unique_filename
        )
        storage_client.upload_file_from_string(storage_key, file_content_str)

        opml_import.storage_key = storage_key
        await self.db.commit()

        return OpmlUploadResponse(
            import_id=import_id,
            filename=filename,
            file_size=file_size,
            message="File uploaded successfully",
        )

    async def import_opml(
        self, request: OpmlImport, user_id: UUID
    ) -> ResponseMessage:
        """Import feeds from previously uploaded OPML file using background processing."""
        opml_import = await self.repository.get_import_by_id(request.import_id)

        if not opml_import or opml_import.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OPML import record not found",
            )

        storage_key = opml_import.storage_key
        if not storage_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OPML file not found. Please upload the file again",
            )

        storage_client = self._get_storage_client()
        if not storage_client.file_exists(storage_key):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OPML file not found or expired. Please upload the file again",
            )

        client = ArqClient()

        try:
            await client.enqueue_job(
                function_name="opml_import",
                job_name="opml_import",
                user_id=str(user_id),
                import_id=str(opml_import.id),
                storage_key=storage_key,
                filename=opml_import.filename,
                folder_id=str(request.folder_id) if request.folder_id else None,
            )
            logger.info(
                "OPML import job enqueued with Arq",
                user_id=user_id,
                import_id=str(opml_import.id),
            )
        except Exception as e:
            logger.exception(
                "Failed to enqueue OPML import job with Arq",
                user_id=user_id,
                import_id=str(opml_import.id),
                error=str(e),
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to queue import job: {e}",
            ) from e

        return ResponseMessage(
            message="OPML import queued successfully. You will be notified when complete."
        )

    async def get_opml_status_by_id(
        self, job_id: UUID, user_id: UUID
    ) -> OpmlOperationResponse:
        """Get detailed OPML import operation info by ID."""
        record = await self.repository.get_opml_by_id(job_id, user_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OPML import operation not found",
            )

        return OpmlOperationResponse(
            id=record.id,
            type="import",
            status=record.status,
            filename=record.filename,
            created_at=record.created_at,
            completed_at=record.completed_at,
            total_feeds=record.total_feeds,
            imported_feeds=record.imported_feeds,
            failed_feeds=record.failed_feeds,
            duplicate_feeds=record.duplicate_feeds,
            failed_feeds_log=record.failed_feeds_log,
        )

    async def rollback_import(self, import_id: UUID, user_id: UUID) -> int:
        """Rollback an OPML import by deleting all subscriptions and orphaned articles."""
        opml_import = await self.repository.get_import_by_id(import_id)
        if not opml_import or opml_import.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Import not found",
            )

        from sqlalchemy import select as sql_select

        select_stmt = sql_select(UserFeed.feed_id).where(
            UserFeed.user_id == user_id,
            UserFeed.import_id == import_id,
        )
        result = await self.db.execute(select_stmt)
        feed_ids = [row[0] for row in result.all()]

        if feed_ids:
            article_ids = await self.user_feed_repo.get_article_ids_for_feeds(
                feed_ids
            )

            accessible_article_ids = await self.user_feed_repo.get_article_ids_accessible_via_other_feeds(
                user_id, article_ids, feed_ids
            )

            articles_to_delete = [
                aid for aid in article_ids if aid not in accessible_article_ids
            ]

            if articles_to_delete:
                await self.tag_repo.remove_articles_from_all_tags(
                    articles_to_delete, user_id
                )

                deleted_articles_count = (
                    await self.user_feed_repo.delete_user_articles(
                        user_id, articles_to_delete
                    )
                )

                logger.info(
                    "Deleted user articles for rolled back feeds (orphaned only)",
                    user_id=str(user_id),
                    import_id=str(import_id),
                    total_articles=len(article_ids),
                    deleted_count=deleted_articles_count,
                    kept_count=len(article_ids) - deleted_articles_count,
                )
            else:
                logger.info(
                    "All articles accessible via other feeds, none deleted",
                    user_id=str(user_id),
                    import_id=str(import_id),
                    total_articles=len(article_ids),
                )

        from sqlalchemy import delete as sql_delete

        stmt = sql_delete(UserFeed).where(
            UserFeed.user_id == user_id,
            UserFeed.import_id == import_id,
        )
        result = await self.db.execute(stmt)
        deleted_count = result.rowcount
        await self.db.commit()

        logger.info(
            "Successfully rolled back OPML import",
            user_id=str(user_id),
            import_id=str(import_id),
            deleted_feeds=deleted_count,
        )

        return deleted_count
