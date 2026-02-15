import type { ListResponse, PaginatedResponse } from '@/types/api'
import type {
	FeedSearchHit,
	FolderSearchHit,
	TagSearchHit,
	UnifiedSearchHit
} from '@/types/search'

// GET '/api/v1/search'
export interface UnifiedSearchQuery {
	q: string
}

// GET '/api/v1/search'
export type UnifiedSearchResponse = ListResponse<UnifiedSearchHit>

// GET '/api/v1/search/feeds'
export interface FeedSearchQuery {
	q: string
	limit?: number
	offset?: number
}

// GET '/api/v1/search/feeds'
export type FeedSearchResponse = PaginatedResponse<FeedSearchHit>

// GET '/api/v1/search/tags'
export interface TagSearchQuery {
	q: string
	limit?: number
	offset?: number
}

// GET '/api/v1/search/tags'
export type TagSearchResponse = PaginatedResponse<TagSearchHit>

// GET '/api/v1/search/folders'
export interface FolderSearchQuery {
	q: string
	limit?: number
	offset?: number
}

// GET '/api/v1/search/folders'
export type FolderSearchResponse = PaginatedResponse<FolderSearchHit>
