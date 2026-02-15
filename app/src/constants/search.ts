import type { SearchType } from '@/types/search'

export const SEARCH_TABS: Array<{ id: SearchType; label: string }> = [
	{ id: 'all', label: 'All' },
	{ id: 'feeds', label: 'Feeds' },
	{ id: 'tags', label: 'Tags' },
	{ id: 'folders', label: 'Folders' }
]
