import type { TagListResponse } from '@/types/api'
import type { ArticleFeedList } from '@/types/content'

// GET '/api/v1/articles'
export interface ArticleListQuery {
	cursor?: string
	subscription_ids?: string[]
	is_read?: 'read' | 'unread' | null
	read_later?: 'true' | 'false' | null
	tag_ids?: string[]
	folder_ids?: string[]
	q?: string
	from_date?: string
	to_date?: string
	limit?: number
}

// GET '/api/v1/articles'
export interface ArticleListResponse {
	id: string
	title: string
	feeds: ArticleFeedList[]
	media_url?: string
	published_at?: string
	is_read: boolean
	read_later: boolean
	summary?: string
}

// GET '/api/v1/articles/{article_id}'
export interface ArticleResponse {
	id: string
	title: string
	feeds: ArticleFeedList[]
	media_url?: string
	published_at?: string
	is_read: boolean
	read_later: boolean
	summary?: string
	author?: string
	canonical_url: string
	tags: TagListResponse[]
	content?: string
	reading_time?: number
	platform_metadata?: PlatformMetadata
}

export interface YouTubeMetadata {
	video_id: string
	channel_id?: string
	duration?: number
	views?: number
	rating?: number
	rating_count?: number
	thumbnail_width?: number
	thumbnail_height?: number
}

export interface PlatformMetadata {
	youtube?: YouTubeMetadata
	podcast?: PodcastMetadata
	// Future: vimeo, spotify, apple_music, etc.
}

export interface PodcastMetadata {
	audio_url: string
	type?: string
	length?: number
}

// PUT '/api/v1/articles/{article_id}'
export interface ArticleStateUpdateRequest {
	is_read?: boolean
	read_later?: boolean
	tag_ids?: string[]
}

// POST '/api/v1/articles/mark-as-read'
// Supports same filtering as GET /api/v1/articles
export interface MarkAllReadRequest {
	is_read: boolean
	subscription_ids?: string[]
	folder_ids?: string[]
	tag_ids?: string[]
	is_read_filter?: 'read' | 'unread' | null
	read_later?: 'true' | 'false' | null
	q?: string
	from_date?: string
	to_date?: string
}
