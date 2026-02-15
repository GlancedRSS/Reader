import type {
	AppLayout,
	ArticleLayout,
	AutoRead,
	DateFormat,
	FeedSortOrder,
	FontSize,
	FontSpacing,
	Language,
	Theme,
	TimeFormat
} from '@/types/settings'

// GET '/api/v1/me'
// PUT '/api/v1/me'
export interface UserResponse {
	username: string
	first_name?: string
	last_name?: string
	is_admin: boolean
	created_at: string
	last_login?: string
}

// PUT '/api/v1/me'
export interface ProfileUpdateRequest {
	first_name?: string
	last_name?: string
}

// GET '/api/v1/me/preferences'
export interface PreferencesResponse {
	theme: Theme
	show_article_thumbnails: boolean
	app_layout: AppLayout
	article_layout: ArticleLayout
	font_spacing: FontSpacing
	font_size: FontSize
	feed_sort_order: FeedSortOrder
	show_feed_favicons: boolean
	date_format: DateFormat
	time_format: TimeFormat
	language: Language
	auto_mark_as_read: AutoRead
	estimated_reading_time: boolean
	show_summaries: boolean
}

// PUT '/api/v1/me/preferences'
export interface PreferencesUpdateRequest {
	theme?: Theme
	show_article_thumbnails?: boolean
	app_layout?: AppLayout
	article_layout?: ArticleLayout
	font_spacing?: FontSpacing
	font_size?: FontSize
	feed_sort_order?: FeedSortOrder
	show_feed_favicons?: boolean
	date_format?: DateFormat
	time_format?: TimeFormat
	language?: Language
	auto_mark_as_read?: AutoRead
	estimated_reading_time?: boolean
	show_summaries?: boolean
}
