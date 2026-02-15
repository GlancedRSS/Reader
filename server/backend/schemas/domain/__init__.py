"""Domain-specific schemas for business logic, API endpoints, and data models."""

from .article import (
    ArticleFeedList,
    ArticleListResponse,
    ArticleResponse,
    ArticleStateUpdateRequest,
    MarkAllReadRequest,
)
from .auth import (
    LoginRequest,
    PasswordChangeRequest,
    RegistrationRequest,
    SessionResponse,
)
from .discovery import (
    FeedDiscoveryRequest,
    FeedDiscoveryResponse,
)
from .feed import (
    UserFeedListResponse,
    UserFeedResponse,
    UserFeedUpdateRequest,
)
from .folder import (
    FeedInFolderResponse,
    FolderCreateRequest,
    FolderListResponse,
    FolderResponse,
    FolderTreeResponse,
    FolderUpdateRequest,
)
from .job import (
    JobCreateResponse,
)
from .opml import (
    OpmlExportRequest,
    OpmlImport,
    OpmlOperationListResponse,
    OpmlOperationResponse,
    OpmlUploadResponse,
)
from .search import (
    MAX_SEARCH_PER_TYPE,
    FeedSearchHit,
    FeedSearchRequest,
    FeedSearchResponse,
    FolderSearchHit,
    FolderSearchRequest,
    FolderSearchResponse,
    TagSearchHit,
    TagSearchRequest,
    TagSearchResponse,
    UnifiedSearchHit,
    UnifiedSearchRequest,
    UnifiedSearchResponse,
)
from .tag import (
    TagCreateRequest,
    TagListResponse,
    TagUpdateRequest,
)
from .user import (
    PreferencesResponse,
    PreferencesUpdateRequest,
    ProfileUpdateRequest,
    UserResponse,
)

__all__ = [
    "MAX_SEARCH_PER_TYPE",
    "ArticleFeedList",
    "ArticleListResponse",
    "ArticleResponse",
    "ArticleStateUpdateRequest",
    "FeedDiscoveryRequest",
    "FeedDiscoveryResponse",
    "FeedInFolderResponse",
    "FeedSearchHit",
    "FeedSearchRequest",
    "FeedSearchResponse",
    "FolderCreateRequest",
    "FolderListResponse",
    "FolderResponse",
    "FolderSearchHit",
    "FolderSearchRequest",
    "FolderSearchResponse",
    "FolderTreeResponse",
    "FolderUpdateRequest",
    "JobCreateResponse",
    "LoginRequest",
    "MarkAllReadRequest",
    "OpmlExportRequest",
    "OpmlImport",
    "OpmlOperationListResponse",
    "OpmlOperationResponse",
    "OpmlUploadResponse",
    "PasswordChangeRequest",
    "PreferencesResponse",
    "PreferencesUpdateRequest",
    "ProfileUpdateRequest",
    "RegistrationRequest",
    "SessionResponse",
    "TagCreateRequest",
    "TagListResponse",
    "TagSearchHit",
    "TagSearchRequest",
    "TagSearchResponse",
    "TagUpdateRequest",
    "UnifiedSearchHit",
    "UnifiedSearchRequest",
    "UnifiedSearchResponse",
    "UserFeedListResponse",
    "UserFeedResponse",
    "UserFeedUpdateRequest",
    "UserResponse",
]
