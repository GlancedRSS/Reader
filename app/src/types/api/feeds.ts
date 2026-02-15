import type { FeedStatus } from '@/types/content'

// GET '/api/v1/feeds'
export interface UserFeedListQuery {
	folder_id?: string
	limit?: number
	offset?: number
	order_by?: 'name' | 'recent'
	cursor?: string
	all?: boolean
}

// GET '/api/v1/feeds'
export interface UserFeedListResponse {
	id: string
	title: string
	unread_count: number
	status: FeedStatus
	website?: string | null
	is_pinned: boolean
	is_active: boolean
}

// GET '/api/v1/feeds/{feed_id}'
export interface UserFeedResponse {
	title: string
	unread_count: number
	status: FeedStatus
	website?: string | null
	is_pinned: boolean
	is_active: boolean
	folder_id?: string
	folder_name?: string
	language?: string
	last_update?: string
	description?: string
	canonical_url?: string
}

// PUT '/api/v1/feeds/{feed_id}'
export interface UserFeedUpdateRequest {
	title?: string
	is_pinned?: boolean
	folder_id?: string | null
	is_active?: boolean
}
