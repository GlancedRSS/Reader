import type { ArticleListResponse } from '@/types/api'

export type SearchType = 'all' | 'feeds' | 'tags' | 'folders'

export interface UnifiedSearchHit {
	type: 'article' | 'feed' | 'tag' | 'folder'
	data: ArticleListResponse | FeedSearchHit | TagSearchHit | FolderSearchHit
}

export interface FeedSearchHit {
	id: string
	title: string
	website: string | null
	is_active: boolean
	is_pinned: boolean
	unread_count: number
}

export interface TagSearchHit {
	id: string
	name: string
	article_count: number
}

export interface FolderSearchHit {
	id: string
	name: string
	unread_count: number
	is_pinned: boolean
}
