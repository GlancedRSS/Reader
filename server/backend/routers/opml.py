"""OPML import/export for feed subscription management."""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse

from backend.core.dependencies import get_opml_application
from backend.core.fastapi import get_user_from_request_state
from backend.infrastructure.external.local_storage import LocalStorageClient
from backend.models import User
from backend.schemas.core import ResponseMessage
from backend.schemas.domain import (
    OpmlExportRequest,
    OpmlImport,
    OpmlOperationResponse,
)

router = APIRouter()


@router.post(
    "/upload",
    response_model=ResponseMessage,
    summary="Upload OPML",
    description="Upload and import OPML file in one step.",
    tags=["OPML"],
)
async def upload_opml(
    file: UploadFile = File(..., description="OPML file to upload"),
    folder_id: UUID | None = Query(
        None, description="Folder ID to import feeds into"
    ),
    current_user: User = Depends(get_user_from_request_state),
    opml_app=Depends(get_opml_application),
) -> ResponseMessage:
    """Upload and import OPML file in one step."""
    file_content = await file.read()
    upload_response = await opml_app.upload_opml_file(
        file_content=file_content,
        filename=file.filename or "upload.opml",
        user_id=current_user.id,
    )

    return await opml_app.import_opml(
        request=OpmlImport(
            import_id=upload_response.import_id,
            folder_id=folder_id,
        ),
        user_id=current_user.id,
    )


@router.post(
    "/export",
    response_model=ResponseMessage,
    summary="Export OPML",
    description="Export user's feeds as OPML using background processing.",
    tags=["OPML"],
)
async def export_opml(
    request: OpmlExportRequest,
    current_user: User = Depends(get_user_from_request_state),
    opml_app=Depends(get_opml_application),
) -> ResponseMessage:
    """Export user's feeds as OPML using background processing."""
    return await opml_app.export_opml(request, current_user.id)


@router.get(
    "/status/{job_id}",
    response_model=OpmlOperationResponse,
    summary="Get OPML operation details",
    description="Get detailed info about an OPML import/export operation by ID.",
    tags=["OPML"],
)
async def get_opml_status(
    job_id: str,
    current_user: User = Depends(get_user_from_request_state),
    opml_app=Depends(get_opml_application),
) -> OpmlOperationResponse:
    """Get detailed OPML operation info by ID."""
    return await opml_app.get_opml_status_by_id(job_id, current_user.id)


@router.post(
    "/{import_id}/rollback",
    response_model=ResponseMessage,
    summary="Rollback OPML import",
    description="Delete all subscriptions created by this OPML import.",
    tags=["OPML"],
)
async def rollback_opml_import(
    import_id: UUID,
    current_user: User = Depends(get_user_from_request_state),
    opml_app=Depends(get_opml_application),
) -> ResponseMessage:
    """Rollback an OPML import by deleting all imported subscriptions."""
    deleted_count = await opml_app.rollback_import(import_id, current_user.id)

    return ResponseMessage(
        message=f"Rolled back {deleted_count} subscriptions",
    )


@router.get(
    "/download/{filename}",
    summary="Download exported OPML file by filename",
    description="Download an exported OPML file using its filename.",
    tags=["OPML"],
)
async def download_opml_by_filename(
    filename: str,
    current_user: User = Depends(get_user_from_request_state),
) -> FileResponse:
    """Download an exported OPML file by filename.

    Verifies ownership by checking the user_id in the storage key path.
    """
    if "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename"
        )

    storage_key = f"users/{current_user.id}/exports/{filename}"
    storage_client = LocalStorageClient()
    file_path = storage_client._base_path / storage_key

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime, tz=UTC)
    file_age_hours = (datetime.now(UTC) - file_mtime).total_seconds() / 3600

    from backend.domain import OPML_FILE_EXPIRY_HOURS

    if file_age_hours > OPML_FILE_EXPIRY_HOURS:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=f"Export file has expired ({OPML_FILE_EXPIRY_HOURS}-hour limit)",
        )

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/xml",
    )
