export type FeedStatus = 'healthy' | 'error' | 'stale'
export type FeedType = 'rss' | 'atom'

export interface ArticleFeedList {
	id: string
	title: string
	website: string
}
