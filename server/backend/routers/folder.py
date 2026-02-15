"""Folder management for hierarchical feed organization."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from backend.core.dependencies import get_folder_application
from backend.core.fastapi import get_user_from_request_state
from backend.domain import DEFAULT_LIMIT, MAX_LIMIT
from backend.models import User
from backend.schemas.core import ResponseMessage
from backend.schemas.domain import (
    FolderCreateRequest,
    FolderListResponse,
    FolderResponse,
    FolderTreeResponse,
    FolderUpdateRequest,
)

router = APIRouter()


@router.get(
    "/tree",
    response_model=list[FolderTreeResponse],
    summary="Get folder tree",
    description="Get complete folder hierarchy with feeds.",
    tags=["Folders"],
)
async def get_folder_tree(
    current_user: User = Depends(get_user_from_request_state),
    folder_app=Depends(get_folder_application),
) -> list[FolderTreeResponse]:
    """Get complete folder hierarchy with feeds."""
    return await folder_app.get_folder_tree(user_id=current_user.id)


@router.get(
    "/{folder_id}",
    response_model=FolderResponse,
    summary="Get folder details",
    description="Get folder details with paginated subfolders.",
    tags=["Folders"],
)
async def get_folder_details(
    folder_id: UUID,
    limit: int = Query(
        DEFAULT_LIMIT,
        ge=1,
        le=MAX_LIMIT,
        description="Number of subfolders to return per page",
    ),
    offset: int = Query(0, ge=0, description="Number of subfolders to skip"),
    current_user: User = Depends(get_user_from_request_state),
    folder_app=Depends(get_folder_application),
) -> FolderResponse:
    """Get folder details with paginated subfolders."""
    return await folder_app.get_folder_details(
        folder_id=folder_id,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=FolderListResponse,
    summary="Create folder",
    description="Create a new folder.",
    tags=["Folders"],
)
async def create_folder(
    folder_data: FolderCreateRequest,
    current_user: User = Depends(get_user_from_request_state),
    folder_app=Depends(get_folder_application),
) -> FolderListResponse:
    """Create a new folder."""
    return await folder_app.create_folder(folder_data, current_user.id)


@router.put(
    "/{folder_id}",
    response_model=ResponseMessage,
    summary="Update folder",
    description="Update folder.",
    tags=["Folders"],
)
async def update_folder(
    folder_id: UUID,
    folder_data: FolderUpdateRequest,
    current_user: User = Depends(get_user_from_request_state),
    folder_app=Depends(get_folder_application),
) -> ResponseMessage:
    """Update folder."""
    return await folder_app.update_folder(
        folder_id, folder_data, current_user.id
    )


@router.delete(
    "/{folder_id}",
    response_model=ResponseMessage,
    summary="Delete folder",
    description="Delete folder.",
    tags=["Folders"],
)
async def delete_folder(
    folder_id: UUID,
    current_user: User = Depends(get_user_from_request_state),
    folder_app=Depends(get_folder_application),
) -> ResponseMessage:
    """Delete folder."""
    return await folder_app.delete_folder(folder_id, current_user.id)
