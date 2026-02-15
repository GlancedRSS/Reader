import type { PreferencesResponse } from '@/types/api'
import type { TabSection } from '@/types/layout'

export const SETTINGS_TABS: TabSection[] = [
	{ id: 'account', label: 'Account', route: '/settings/account' },
	{ id: 'preferences', label: 'Preferences', route: '/settings/preferences' }
]

export const THEME_OPTIONS = [
	{
		id: 'light',
		name: 'Light'
	},
	{
		id: 'dark',
		name: 'Dark'
	},
	{ id: 'system', name: 'System' }
]

export const LANGUAGES = [
	{ code: 'en', name: 'English' },
	{ code: 'es', name: 'Español' },
	{ code: 'fr', name: 'Français' },
	{ code: 'de', name: 'Deutsch' },
	{ code: 'it', name: 'Italiano' },
	{ code: 'pt', name: 'Português' },
	{ code: 'ru', name: 'Русский' },
	{ code: 'zh', name: '中文' },
	{ code: 'ja', name: '日本語' },
	{ code: 'ko', name: '한국어' }
]

export const DATE_FORMAT_OPTIONS = [
	{ label: 'Relative', value: 'relative' },
	{ label: 'Absolute', value: 'absolute' }
]

export const TIME_FORMAT_OPTIONS = [
	{ label: '12-hour', value: '12h' },
	{ label: '24-hour', value: '24h' }
]

export const DEFAULT_USER_PREFERENCES: PreferencesResponse = {
	app_layout: 'split',
	article_layout: 'grid',
	auto_mark_as_read: 'disabled',
	date_format: 'relative',
	estimated_reading_time: true,
	feed_sort_order: 'recent_first',
	font_size: 'm',
	font_spacing: 'normal',
	language: 'en',
	show_article_thumbnails: true,
	show_feed_favicons: true,
	show_summaries: true,
	theme: 'system',
	time_format: '12h'
}

export const APP_LAYOUT_OPTIONS = [
	{ label: 'Split', value: 'split' },
	{ label: 'Focus', value: 'focus' }
]

export const ARTICLE_LAYOUT_OPTIONS = [
	{ label: 'Grid', value: 'grid' },
	{ label: 'List', value: 'list' },
	{ label: 'Magazine', value: 'magazine' }
]

export const FEED_SORT_ORDER_OPTIONS = [
	{ label: 'Latest First', value: 'recent_first' },
	{ label: 'Alphabetical', value: 'alphabetical' }
]

export const FONT_SIZE_OPTIONS = [
	{ label: 'Extra Small', value: 'xs' },
	{ label: 'Small', value: 's' },
	{ label: 'Medium', value: 'm' },
	{ label: 'Large', value: 'l' },
	{ label: 'Extra Large', value: 'xl' }
]

export const FONT_SPACING_OPTIONS = [
	{ label: 'Compact', value: 'compact' },
	{ label: 'Normal', value: 'normal' },
	{ label: 'Comfortable', value: 'comfortable' }
]

export const AUTO_READ_OPTIONS = [
	{ label: 'Disabled', value: 'disabled' },
	{ label: '7 days', value: '7_days' },
	{ label: '14 days', value: '14_days' },
	{ label: '30 days', value: '30_days' }
]

export const SELECT_WIDTHS = {
	LONG: 'w-48',
	MEDIUM: 'w-40',
	SHORT: 'w-32'
} as const
